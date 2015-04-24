from business.models import Employee, EmployeeToken, Staff, StaffToken
from customers.models import Order, OrderedFood, User
from lunch.models import DefaultIngredient, Food, IngredientGroup
from lunch.serializers import (DefaultFoodSerializer,
                               DefaultIngredientSerializer, FoodSerializer,
                               ShortDefaultIngredientRelationSerializer,
                               StoreSerializer, TokenSerializer)
from rest_framework import serializers


class BusinessTokenSerializer(TokenSerializer):
    password = serializers.CharField(max_length=128, write_only=True)
    device = serializers.CharField(max_length=128, write_only=True)

    class Meta:
        fields = TokenSerializer.Meta.fields + ('password', 'device',)
        write_only_fields = ('password', 'device',)
        read_only_fields = ()


class StaffSerializer(serializers.ModelSerializer):
    store = StoreSerializer()

    class Meta:
        model = Staff
        fields = ('id', 'store', 'password',)
        read_only_fields = ('id',)
        write_only_fields = ('password',)


class StaffTokenSerializer(BusinessTokenSerializer):

    class Meta:
        model = StaffToken
        fields = BusinessTokenSerializer.Meta.fields + ('staff',)
        read_only_fields = BusinessTokenSerializer.Meta.read_only_fields + ('staff',)


class EmployeeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Employee
        fields = ('id', 'name', 'password',)
        read_only_fields = ('id',)
        write_only_fields = ('password',)


class EmployeeTokenSerializer(BusinessTokenSerializer):

    class Meta:
        model = EmployeeToken
        fields = BusinessTokenSerializer.Meta.fields + ('employee',)
        read_only_fields = BusinessTokenSerializer.Meta.read_only_fields + ('employee',)


class PrivateUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'name',)


class OrderedFoodSerializer(serializers.ModelSerializer):
    cost = serializers.DecimalField(decimal_places=2, max_digits=5)

    class Meta:
        model = OrderedFood
        fields = ('id', 'ingredients', 'amount', 'original', 'cost')
        read_only_fields = fields


class ShortOrderSerializer(serializers.ModelSerializer):
    user = PrivateUserSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'user', 'orderedTime', 'pickupTime', 'status', 'paid', 'total',)
        read_only_fields = ('id', 'user', 'orderedTime', 'pickupTime', 'paid', 'total',)


class OrderSerializer(ShortOrderSerializer):
    orderedFood = OrderedFoodSerializer(many=True, read_only=True, source="orderedfood_set")

    class Meta:
        model = Order
        fields = ShortOrderSerializer.Meta.fields + ('orderedFood',)
        read_only_fields = ShortOrderSerializer.Meta.read_only_fields + ('orderedFood',)


class ShortIngredientGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = IngredientGroup
        fields = ('id', 'name', 'maximum', 'priority',)
        read_only_fields = ('id', 'name', 'maximum', 'priority',)


class ShortFoodSerializer(serializers.ModelSerializer):
    ingredients = ShortDefaultIngredientRelationSerializer(source='ingredientrelation_set', many=True)

    class Meta:
        model = Food
        fields = ('id', 'name', 'category', 'foodType', 'ingredients',)
        read_only_fields = ('id', 'name', 'category', 'foodType', 'ingredients',)


class StoreFoodSerializer(FoodSerializer):
    class Meta:
        model = Food
        fields = DefaultFoodSerializer.Meta.fields
        read_only_fields = DefaultFoodSerializer.Meta.read_only_fields


class SingleIngredientSerializer(DefaultIngredientSerializer):

    class Meta:
        model = DefaultIngredient
        fields = DefaultIngredientSerializer.Meta.fields + ('group',)
