from customers.authentication import CustomerAuthentication
from customers.digits import Digits
from customers.models import Heart, Order, OrderedFood, User, UserToken
from customers.serializers import (OrderedFoodPriceSerializer, OrderSerializer,
                                   ShortOrderSerializer, UserSerializer,
                                   UserTokenSerializer)
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from lunch.exceptions import LunchbreakException
from lunch.models import Food, IngredientGroup, Store, tokenGenerator
from lunch.responses import BadRequest
from lunch.serializers import (FoodSerializer, HolidayPeriodSerializer,
                               OpeningHoursSerializer,
                               ShortDefaultFoodSerializer, StoreSerializer)
from lunch.views import (getHolidayPeriods, getOpeningAndHoliday,
                         getOpeningHours, StoreCategoryListViewBase)
from rest_framework import generics, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404


class StoreListView(generics.ListAPIView):
    '''
    List the stores.
    '''

    authentication_classes = (CustomerAuthentication,)
    serializer_class = StoreSerializer

    def get_queryset(self):
        proximity = self.kwargs['proximity'] if 'proximity' in self.kwargs else 5
        if 'latitude' in self.kwargs and 'longitude' in self.kwargs:
            return Store.objects.nearby(self.kwargs['latitude'], self.kwargs['longitude'], proximity)
        elif 'id' in self.kwargs:
            return Store.objects.filter(id=self.kwargs['id'])


class StoreHeartView(generics.UpdateAPIView):
    '''
    Heart or unheart a store.
    '''

    authentication_classes = (CustomerAuthentication,)
    queryset = Heart.objects.all()


    def update(self, request, *args, **kwargs):
        like = 'store_like' in self.kwargs
        storeId = self.kwargs['store_like'] if like else self.kwargs['store_dislike']
        store = Store.objects.get(id=storeId)

        if like:
            heart, created = Heart.objects.get_or_create(store=store, user=request.user)
            statusCode = status.HTTP_201_CREATED if created else status.HTTP_200_OK
            return Response(status=statusCode)
        else:
            heart = get_object_or_404(Heart, store=store, user=request.user)
            heart.delete()
            return Response(status=status.HTTP_200_OK)



class StoreOpenView(generics.ListAPIView):
    '''
    List the opening hours and holiday periods of a store.
    '''

    authentication_classes = (CustomerAuthentication,)
    serializer_class = OpeningHoursSerializer
    pagination_class = None
    queryset = None

    def get(self, request, *args, **kwargs):
        return getOpeningAndHoliday(self.kwargs['store_id'])


class StoreCategoryListView(StoreCategoryListViewBase):
    authentication_classes = (CustomerAuthentication,)


class OpeningHoursListView(generics.ListAPIView):
    '''
    List the opening hours of a store.
    '''

    authentication_classes = (CustomerAuthentication,)
    serializer_class = OpeningHoursSerializer
    pagination_class = None

    def get_queryset(self):
        return getOpeningHours(self.kwargs['store_id'])


class HolidayPeriodListView(generics.ListAPIView):
    '''
    List the holiday periods of a store.
    '''

    authentication_classes = (CustomerAuthentication,)
    serializer_class = HolidayPeriodSerializer
    pagination_class = None

    def get_queryset(self):
        return getHolidayPeriods(self.kwargs['store_id'])


class FoodListView(generics.ListAPIView):
    '''
    List the available food.
    '''

    authentication_classes = (CustomerAuthentication,)
    serializer_class = ShortDefaultFoodSerializer

    def get_queryset(self):
        if 'store_id' in self.kwargs:
            return Food.objects.filter(store_id=self.kwargs['store_id'])


class FoodRetrieveView(generics.RetrieveAPIView):
    '''
    Retrieve a specific food.
    '''

    serializer_class = FoodSerializer
    queryset = Food.objects.all()

    authentication_classes = (CustomerAuthentication,)


class OrderView(generics.ListCreateAPIView):
    '''
    Place an order and list a specific or all of the user's orders.
    '''

    authentication_classes = (CustomerAuthentication,)
    serializer_class = ShortOrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-pickupTime')

    def create(self, request, *args, **kwargs):
        orderSerializer = ShortOrderSerializer(data=request.data, context={'user': request.user})
        if orderSerializer.is_valid():
            try:
                orderSerializer.save()
            except LunchbreakException as e:
                return e.getResponse()
            else:
                return Response(data=orderSerializer.data, status=status.HTTP_201_CREATED)
        return BadRequest(orderSerializer.errors)


class OrderRetrieveView(generics.RetrieveAPIView):
    '''
    Retrieve a single order.
    '''

    authentication_classes = (CustomerAuthentication,)
    serializer_class = OrderSerializer
    queryset = Order.objects.all()


class OrderPriceView(generics.CreateAPIView):
    authentication_classes = (CustomerAuthentication,)
    serializer_class = OrderedFoodPriceSerializer

    def post(self, request, format=None):
        '''
        Return the price of the food.
        '''
        priceSerializer = OrderedFoodPriceSerializer(data=request.data, many=True)
        if priceSerializer.is_valid():
            result = []
            for priceCheck in priceSerializer.validated_data:
                priceInfo = {}
                original = priceCheck['original']
                if 'ingredients' in priceCheck:
                    ingredients = priceCheck['ingredients']
                    IngredientGroup.checkIngredients(ingredients, original.foodType)
                    closestFood = Food.objects.closestFood(ingredients, original)

                    priceInfo['cost'] = OrderedFood.calculateCost(ingredients, closestFood)
                    priceInfo['food'] = closestFood.id
                else:
                    priceInfo['cost'] = original.cost
                    priceInfo['food'] = original.id
                result.append(priceInfo)
            return Response(data=result, status=status.HTTP_200_OK)
        return BadRequest(priceSerializer.errors)


class UserTokenView(generics.ListAPIView):
    '''
    Tokens can only be listed (for now).
    '''

    authentication_classes = (CustomerAuthentication,)
    serializer_class = UserTokenSerializer

    def get_queryset(self):
        '''
        Return all of the Tokens for the authenticated user.
        '''
        return UserToken.objects.filter(user=self.request.user)


class UserView(generics.CreateAPIView):

    serializer_class = UserSerializer

    # For all these methods a try-except is not needed since a DigitsException is generated
    # which will provide everything
    def register(self, digits, phone):
        try:
            digits.register(phone)
            return True
        except:
            return self.signIn(digits, phone)

    def signIn(self, digits, phone):
        content = digits.signin(phone)
        return {
            'digitsId': content['login_verification_user_id'],
            'requestId': content['login_verification_request_id']
        }

    def confirmRegistration(self, digits, phone, pin):
        content = digits.confirmRegistration(phone, pin)
        return content['id']

    def confirmSignin(self, digits, requestId, digitsId, pin):
        digits.confirmSignin(requestId, digitsId, pin)
        return True

    def getRegistrationResponse(self, hasName=False):
        if hasName:
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_201_CREATED)

    def createGetToken(self, user, device, name):
        token, created = UserToken.objects.get_or_create(device=device, user=user)
        if not created:
            token.identifier = tokenGenerator()
        token.save()
        tokenSerializer = UserTokenSerializer(token)
        return Response(tokenSerializer.data, status=(status.HTTP_201_CREATED if created else status.HTTP_200_OK))

    def create(self, request, *args, **kwargs):
        userSerializer = UserSerializer(data=request.data)
        if userSerializer.is_valid():
            phone = request.data.__getitem__('phone')
            queryset = User.objects.filter(phone=phone)
            digits = Digits()
            if not queryset:
                result = self.register(digits, phone)
                if result:
                    user = User(phone=phone)
                    if type(result) is dict:
                        user.digitsId = result['digitsId']
                        user.requestId = result['requestId']
                    user.save()
                    return self.getRegistrationResponse()
            else:
                pin = request.data.get('pin', False)
                user = queryset[0]
                hasName = user.name != ''
                givenName = request.data.get('name', False)
                name = givenName if givenName else user.name
                if not pin:
                    # The user is in the database, but isn't sending a pin code so he's trying to signin/register
                    if user.confirmedAt:
                        result = self.signIn(digits, phone)
                        if result:
                            user.digitsId = result['digitsId']
                            user.requestId = result['requestId']
                            user.save()
                            return self.getRegistrationResponse(hasName)
                    else:
                        result = self.register(digits, phone)
                        if result:
                            if type(result) is dict:
                                user.digitsId = result['digitsId']
                                user.requestId = result['requestId']
                            user.save()
                            return self.getRegistrationResponse(hasName)
                elif name:
                    device = request.data.get('device', False)
                    user.name = name
                    success = False
                    if device:
                        if not user.confirmedAt:
                            user.confirmedAt = timezone.now()

                        if not user.requestId and not user.digitsId:
                            # The user already got a message, but just got added to the Digits database
                            user.digitsId = self.confirmRegistration(digits, phone, pin)
                            user.save()
                            success = True
                        else:
                            # The user already was in the Digits database and got a request and user id
                            self.confirmSignin(digits, user.requestId, user.digitsId, pin)
                            user.save()
                            success = True

                        if success:
                            return self.createGetToken(user, device, name)
        elif request.data.get('phone', False) == '+32411111111':
            if 'pin' not in request.data:
                return Response(status=status.HTTP_200_OK)

            if 'device' in request.data:
                try:
                    demoUser = User.objects.get(phone=request.data['phone'], requestId=request.data['pin'], digitsId='demo', )
                except ObjectDoesNotExist:
                    pass
                else:
                    return self.createGetToken(demoUser, request.data['device'], 'demo')
        return BadRequest(userSerializer.errors)
