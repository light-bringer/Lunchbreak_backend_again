from customers.config import RESERVATION_STATUS_EMPLOYEE
from customers.models import Order, OrderedFood, Reservation, User
from lunch import serializers as lunch_serializers
from lunch.config import TOKEN_IDENTIFIER_LENGTH
from lunch.models import (BaseToken, Food, Ingredient, IngredientGroup,
                          IngredientRelation, Store)
from rest_framework import serializers

from .models import (AbstractPassword, Employee, EmployeeToken, Staff,
                     StaffToken)


class StoreSerializer(serializers.ModelSerializer):
    categories = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True
    )

    class Meta:
        model = Store
        fields = (
            'id',
            'name',
            'city',
            'street',
            'latitude',
            'longitude',
            'categories',
            'hearts_count',
            'country',
            'province',
            'city',
            'postcode',
            'street',
            'number',
            'wait',
            'preorder_time',
            'enabled',
        )
        read_only_fields = (
            'id',
            'latitude',
            'longitude',
            'hearts_count',
            'categories',
        )


class StoreSerializerV3(StoreSerializer):

    class Meta:
        model = Store
        fields = StoreSerializer.Meta.fields
        read_only_fields = StoreSerializer.Meta.read_only_fields

    def save(self):
        if 'wait' in self.validated_data:
            self.validated_data['wait'] *= 60
        super(StoreSerializer, self).save()


class EmployeePasswordRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = Employee
        fields = ('id',)
        write_only_fields = fields


class StaffPasswordRequestSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        max_length=255
    )

    class Meta:
        model = Staff
        fields = ('email',)
        write_only_fields = fields


class PasswordSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        max_length=255,
        write_only=True
    )
    password_reset = serializers.CharField(
        max_length=TOKEN_IDENTIFIER_LENGTH,
        write_only=True
    )

    class Meta:
        model = AbstractPassword
        fields = (
            'password',
            'password_reset',
            'email',
        )
        write_only_fields = fields


class EmployeePasswordSerializer(PasswordSerializer):

    class Meta:
        model = Employee
        fields = PasswordSerializer.Meta.fields
        write_only_fields = PasswordSerializer.Meta.write_only_fields


class StaffPasswordSerializer(PasswordSerializer):

    class Meta:
        model = Staff
        fields = PasswordSerializer.Meta.fields
        write_only_fields = PasswordSerializer.Meta.write_only_fields


class BusinessTokenSerializer(lunch_serializers.TokenSerializer):
    password = serializers.CharField(
        max_length=255,
        write_only=True
    )

    class Meta:
        model = BaseToken
        fields = lunch_serializers.TokenSerializer.Meta.fields + (
            'password',
        )
        write_only_fields = (
            'password',
        )
        read_only_fields = (
            'id',
            'identifier',
            'active',
        )


class StaffSerializer(serializers.ModelSerializer):
    store = StoreSerializer()

    class Meta:
        model = Staff
        fields = (
            'id',
            'store',
        )
        read_only_fields = (
            'id',
        )


class StaffTokenSerializer(BusinessTokenSerializer):

    class Meta:
        model = StaffToken
        fields = BusinessTokenSerializer.Meta.fields + (
            'staff',
        )
        read_only_fields = BusinessTokenSerializer.Meta.read_only_fields
        write_only_fields = BusinessTokenSerializer.Meta.write_only_fields


class EmployeeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Employee
        fields = (
            'id',
            'name',
            'owner',
        )
        read_only_fields = (
            'id',
        )


class EmployeeTokenSerializer(BusinessTokenSerializer):

    class Meta:
        model = EmployeeToken
        fields = BusinessTokenSerializer.Meta.fields + (
            'employee',
        )
        read_only_fields = BusinessTokenSerializer.Meta.read_only_fields
        write_only_fields = BusinessTokenSerializer.Meta.write_only_fields


class PrivateUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'name',)


class OrderedFoodSerializer(serializers.ModelSerializer):
    cost = serializers.DecimalField(
        decimal_places=2,
        max_digits=7
    )

    class Meta:
        model = OrderedFood
        fields = (
            'id',
            'ingredients',
            'amount',
            'original',
            'cost',
            'is_original',
            'comment',
        )
        read_only_fields = fields


class ShortOrderSerializer(serializers.ModelSerializer):
    user = PrivateUserSerializer(
        read_only=True
    )

    class Meta:
        model = Order
        fields = (
            'id',
            'user',
            'placed',
            'pickup',
            'status',
            'total',
            'total_confirmed',
        )
        read_only_fields = (
            'id',
            'user',
            'placed',
            'pickup',
            'total',
            'total_confirmed',
        )


class OrderSpreadSerializer(serializers.BaseSerializer):
    amount = serializers.IntegerField(
        read_only=True
    )
    average = serializers.DecimalField(
        decimal_places=2,
        max_digits=7
    )
    # 'sum' is a built-in function in Python, use 'sm' in code and return 'sum'
    sm = serializers.DecimalField(
        decimal_places=2,
        max_digits=7
    )
    unit = serializers.IntegerField(
        read_only=True
    )

    class Meta:
        fields = (
            'amount',
            'average',
            'sm',
            'unit',
        )
        read_only_fields = fields

    def to_representation(self, obj):
        return {
            'amount': obj.amount,
            'average': obj.average,
            'sum': obj.sm,
            'unit': obj.unit
        }


class OrderSerializer(ShortOrderSerializer):
    orderedfood = OrderedFoodSerializer(
        many=True,
        read_only=True,
        source='orderedfood_set'
    )

    class Meta:
        model = Order
        fields = ShortOrderSerializer.Meta.fields + (
            'orderedfood',
            'description',
        )
        read_only_fields = (
            'id',
            'user',
            'placed',
            'pickup',
            'total',
            'orderedfood',
            'description',
        )


class ShortIngredientGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = IngredientGroup
        fields = (
            'id',
            'name',
            'maximum',
            'minimum',
            'priority',
            'cost',
            'foodtype',
        )
        read_only_fields = (
            'id',
        )


class IngredientRelationSerializer(serializers.ModelSerializer):
    ingredient = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = IngredientRelation
        fields = (
            'ingredient',
            'selected',
        )
        write_only_fields = fields


class ShortFoodSerializer(serializers.ModelSerializer):
    ingredients = lunch_serializers.ShortIngredientRelationSerializer(
        source='ingredientrelation_set',
        many=True,
        required=False,
        read_only=True
    )
    ingredientrelations = IngredientRelationSerializer(
        source='ingredientrelation_set',
        many=True,
        required=False,
        write_only=True
    )
    orderedfood_count = serializers.IntegerField(
        read_only=True
    )

    class Meta:
        model = Food
        fields = (
            'id',
            'name',
            'description',
            'amount',
            'cost',
            'foodtype',
            'preorder_days',
            'commentable',
            'priority',

            'category',
            'ingredients',
            'ingredientgroups',

            'ingredientrelations',
            'orderedfood_count',
            'deleted',
        )
        read_only_fields = (
            'id',
            'ingredients',
            'orderedfood_count',
        )
        write_only_fields = (
            'ingredientrelations',
        )

    def create_or_update(self, validated_data, food=None):
        update = food is not None
        relations = validated_data.pop('ingredientrelation_set', None)

        if not update:
            food = super(ShortFoodSerializer, self).create(validated_data)
        else:
            food = super(ShortFoodSerializer, self).update(food, validated_data)

        if relations is not None:
            if update:
                IngredientRelation.objects.filter(food=food).delete()
            for relation in relations:
                IngredientRelation.objects.update_or_create(
                    food=food,
                    **relation
                )

        return food

    def create(self, validated_data):
        return self.create_or_update(validated_data)

    def update(self, instance, validated_data):
        return self.create_or_update(validated_data, instance)


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'cost',
            'group',
        )
        read_only_fields = (
            'id',
        )


class IngredientGroupSerializer(serializers.ModelSerializer):
    ingredients = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True
    )

    class Meta:
        model = IngredientGroup
        fields = (
            'id',
            'name',
            'maximum',
            'minimum',
            'ingredients',
            'priority',
            'cost',
            'foodtype',
        )
        read_only_fields = (
            'id',
            'ingredients',
        )


class SingleFoodSerializer(lunch_serializers.SingleFoodSerializer):

    class Meta:
        model = lunch_serializers.SingleFoodSerializer.Meta.model
        fields = lunch_serializers.SingleFoodSerializer.Meta.fields + (
            'deleted',
        )
        read_only_fields = lunch_serializers.SingleFoodSerializer.Meta.read_only_fields


class ReservationSerializer(serializers.ModelSerializer):
    user = PrivateUserSerializer(
        read_only=True
    )
    status = serializers.ChoiceField(
        choices=RESERVATION_STATUS_EMPLOYEE
    )

    class Meta:
        model = Reservation
        fields = (
            'id',
            'user',
            'seats',
            'placed',
            'reservation_time',
            'comment',
            'suggestion',
            'response',
            'status',
        )
        read_only_fields = (
            'id',
            'user',
            'placed',
            'reservation_time',
            'comment',
        )
