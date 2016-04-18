from __future__ import unicode_literals

import copy
from datetime import datetime, time, timedelta

import googlemaps
from customers.config import ORDER_STATUSES_ENDED
from customers.exceptions import MinTimeExceeded, PastOrderDenied, StoreClosed
from dirtyfields import DirtyFieldsMixin
from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.core.exceptions import MultipleObjectsReturned, ValidationError
from django.core.validators import MinValueValidator
from django.db import DatabaseError, models
from django.db.models.signals import m2m_changed
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from imagekit.models import ImageSpecField
from openpyxl import load_workbook
from polaroid.models import Polaroid
from private_media.storages import PrivateMediaStorage
from push_notifications.models import BareDevice, DeviceManager

from .config import (CCTLDS, COST_GROUP_ALWAYS, COST_GROUP_CALCULATIONS,
                     COUNTRIES, ICONS, INPUT_AMOUNT, INPUT_SI_VARIABLE,
                     INPUT_TYPES, LANGUAGES, WEEKDAYS, random_token)
from .exceptions import (AddressNotFound, IngredientGroupMaxExceeded,
                         IngredientGroupsMinimumNotMet, InvalidFoodTypeAmount,
                         LinkingError)
from .managers import FoodManager, StoreManager
from .specs import HDPI, LDPI, MDPI, XHDPI, XXHDPI, XXXHDPI


class StoreCategory(models.Model):
    name = models.CharField(
        max_length=255
    )
    icon = models.PositiveIntegerField(
        choices=ICONS,
        default=ICONS[0][0]
    )

    class Meta:
        verbose_name_plural = 'Store categories'

    def __unicode__(self):
        return self.name


class StoreHeader(Polaroid):
    original = models.ImageField(
        storage=PrivateMediaStorage(),
        upload_to='storeheader'
    )
    ldpi = ImageSpecField(
        spec=LDPI,
        source='original'
    )
    mdpi = ImageSpecField(
        spec=MDPI,
        source='original'
    )
    hdpi = ImageSpecField(
        spec=HDPI,
        source='original'
    )
    xhdpi = ImageSpecField(
        spec=XHDPI,
        source='original'
    )
    xxhdpi = ImageSpecField(
        spec=XXHDPI,
        source='original'
    )
    xxxhdpi = ImageSpecField(
        spec=XXXHDPI,
        source='original'
    )


class AbstractAddress(models.Model, DirtyFieldsMixin):
    country = models.CharField(
        max_length=255
    )
    province = models.CharField(
        max_length=255
    )
    city = models.CharField(
        max_length=255
    )
    postcode = models.CharField(
        max_length=20,
        verbose_name=_('Postal code')
    )
    street = models.CharField(
        max_length=255
    )
    number = models.CharField(
        max_length=10
    )

    latitude = models.DecimalField(
        decimal_places=7,
        max_digits=10
    )
    longitude = models.DecimalField(
        decimal_places=7,
        max_digits=10
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        dirty_fields = self.get_dirty_fields()
        fields = [
            'country',
            'province',
            'city',
            'postcode',
            'street',
            'number',
            'latitude',
            'longitude'
        ]

        if self.pk is None or dirty_fields:
            update_location = False
            if self.pk is not None and dirty_fields:
                for field in fields:
                    if field in dirty_fields:
                        update_location = True
                        break
            else:
                update_location = True

            if update_location:
                self.clean_fields(
                    exclude=[
                        'latitude',
                        'longitude'
                    ]
                )

                google_client = googlemaps.Client(
                    key=settings.GOOGLE_CLOUD_SECRET,
                    connect_timeout=5,
                    read_timeout=5,
                    retry_timeout=1
                )
                address = '{country}, {province}, {street} {number}, {postcode} {city}'.format(
                    country=self.country,
                    province=self.province,
                    street=self.street,
                    number=self.number,
                    postcode=self.postcode,
                    city=self.city,
                )
                results = google_client.geocode(
                    address=address
                )

                if len(results) == 0:
                    raise AddressNotFound(
                        _('No results found for given postcode and country.')
                    )

                result = results[0]
                self.latitude = result['geometry']['location']['lat']
                self.longitude = result['geometry']['location']['lng']

        self.full_clean()
        super(AbstractAddress, self).save(*args, **kwargs)


class Store(AbstractAddress):
    name = models.CharField(
        max_length=255
    )
    header = models.ForeignKey(
        StoreHeader,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    categories = models.ManyToManyField(
        StoreCategory
    )
    wait = models.DurationField(
        default=timedelta(seconds=60)
    )
    preorder_time = models.TimeField(
        default=time(hour=12)
    )
    hearts = models.ManyToManyField(
        'customers.User',
        through='customers.Heart',
        blank=True
    )
    seats_max = models.PositiveIntegerField(
        default=10,
        validators=[
            MinValueValidator(1)
        ]
    )
    regions = models.ManyToManyField(
        'Region',
        help_text=_('Active delivery regions.')
    )

    last_modified = models.DateTimeField(
        auto_now=True
    )
    enabled = models.BooleanField(
        default=True
    )

    objects = StoreManager()

    def __unicode__(self):
        return '{name}, {city}'.format(
            name=self.name,
            city=self.city
        )

    @cached_property
    def hearts_count(self):
        return self.hearts.count()

    def delivers_to(self, address):
        return self.regions.filter(
            postcode=address.postcode
        ).exists()

    @staticmethod
    def check_open(store, pickup, now=None):
        """Check whether the store is open at the specified time."""

        now = timezone.now() if now is None else now

        if pickup < now:
            raise PastOrderDenied()

        if pickup - now < store.wait:
            raise MinTimeExceeded()

        holidayperiods = HolidayPeriod.objects.filter(
            store=store,
            start__lte=pickup,
            end__gte=pickup
        )

        closed = False
        for holidayperiod in holidayperiods:
            if not holidayperiod.closed:
                break
            else:
                closed = True
        else:
            # Open stores are
            if closed:
                raise StoreClosed()

            openingperiods = OpeningPeriod.objects.filter(
                store=store
            )

            for openingperiod in openingperiods:
                if openingperiod.contains(pickup):
                    return
            raise StoreClosed()


class Region(models.Model):
    name = models.CharField(
        max_length=255
    )
    country = models.PositiveSmallIntegerField(
        choices=COUNTRIES
    )
    postcode = models.CharField(
        max_length=255
    )

    class Meta:
        unique_together = ('country', 'postcode',)

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.validate_unique()
            self.clean_fields(
                exclude=[
                    'name'
                ]
            )

            google_client = googlemaps.Client(
                key=settings.GOOGLE_CLOUD_SECRET,
                connect_timeout=5,
                read_timeout=5,
                retry_timeout=1
            )
            results = google_client.geocode(
                address=self.postcode,
                components={
                    'country': self.get_country_display()
                },
                region=CCTLDS[self.country],
                language=LANGUAGES[self.country]
            )
            if len(results) == 0:
                raise AddressNotFound(
                    _('No results found for given postcode and country.')
                )
            address_components = results[0].get('address_components', [])
            found = False
            for comp in address_components:
                types = comp.get('types', [])
                if 'locality' in types:
                    self.name = comp['long_name']
                    found = True
            if not found:
                raise AddressNotFound(
                    _('No region found for given postcode and country.')
                )

        self.full_clean()
        super(Region, self).save(*args, **kwargs)

    def __unicode__(self):
        return '{country}, {name} {postcode}'.format(
            country=self.get_country_display(),
            name=self.name,
            postcode=self.postcode
        )


class Period(models.Model):
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE
    )

    opening_day = models.PositiveSmallIntegerField(
        choices=WEEKDAYS
    )
    closing_day = models.PositiveSmallIntegerField(
        choices=WEEKDAYS
    )

    opening_time = models.TimeField()
    closing_time = models.TimeField()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.store.save()
        super(Period, self).save(*args, **kwargs)

    @classmethod
    def _is_between_days(cls, given_day, given_time, start_day, start_time,
                         end_day, end_time):
        """Returns True if given day and time is between start and end days and times.

        ..note:
            This assumes the days are 0-6 (weekly).
        """

        if start_day <= given_day <= end_day:
            if start_day == end_day:
                return given_day == start_day and start_time < given_time < end_time
            else:  # start_day < end_day
                if given_day == start_day:
                    return start_time < given_time
                elif given_day == end_day:
                    return given_time < end_time
                return True  # start_day < given_day < end_day
        elif end_day < start_day:
            return not cls._is_between_days(
                given_day=given_day,
                given_time=given_time,
                start_day=end_day,
                start_time=end_time,
                end_day=start_day,
                end_time=start_time
            )
        return False

    def contains(self, dt):
        """Return True if dt (datetime) is in the period."""

        # datetime.weekday(): return monday 0 - sunday 6
        # datetime.strftime('%w'): return sunday 0 - saturday 6
        given_day = int(dt.strftime('%w'))
        given_time = dt.time()

        return self._is_between_days(
            given_day=given_day,
            given_time=given_time,
            start_day=self.opening_day,
            start_time=self.opening_time,
            end_day=self.closing_day,
            end_time=self.closing_time
        )

    def __unicode__(self):
        return '{opening_day} {opening_time} - {closing_day} {closing_time}'.format(
            opening_day=self.get_opening_day_display(),
            opening_time=self.opening_time,
            closing_day=self.get_closing_day_display(),
            closing_time=self.closing_time
        )


class OpeningPeriod(Period):
    pass


class DeliveryPeriod(Period):
    pass


class HolidayPeriod(models.Model):
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE
    )
    description = models.CharField(
        max_length=255,
        blank=True
    )

    start = models.DateTimeField()
    end = models.DateTimeField()

    closed = models.BooleanField(
        default=True
    )

    def clean(self):
        if self.start >= self.end:
            raise ValidationError('Start needs to be before end.')

    def save(self, *args, **kwargs):
        self.full_clean()
        self.store.save()
        super(HolidayPeriod, self).save(*args, **kwargs)

    def __unicode__(self):
        return '{start}-{end} {state}'.format(
            start=self.start,
            end=self.end,
            state='closed' if self.closed else 'open'
        )


class FoodType(models.Model):
    name = models.CharField(
        max_length=255
    )
    quantifier = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    inputtype = models.PositiveIntegerField(
        choices=INPUT_TYPES,
        default=INPUT_TYPES[0][0]
    )
    customisable = models.BooleanField(
        default=False
    )

    def is_valid_amount(self, amount, quantity=None):
        return (
            amount > 0 and
            (self.inputtype != INPUT_AMOUNT or float(amount).is_integer()) and
            (quantity is None or quantity.min <= amount <= quantity.max)
        )

    def __unicode__(self):
        return self.name


class IngredientGroup(models.Model):
    name = models.CharField(
        max_length=255
    )
    foodtype = models.ForeignKey(
        FoodType,
        on_delete=models.CASCADE
    )
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE
    )

    maximum = models.PositiveIntegerField(
        default=0,
        verbose_name='Maximum amount'
    )
    minimum = models.PositiveIntegerField(
        default=0,
        verbose_name='Minimum amount'
    )
    priority = models.PositiveIntegerField(
        default=0
    )
    cost = models.DecimalField(
        default=0,
        validators=[
            MinValueValidator(0)
        ],
        max_digits=7,
        decimal_places=2
    )
    calculation = models.PositiveIntegerField(
        choices=COST_GROUP_CALCULATIONS,
        default=COST_GROUP_ALWAYS
    )

    def clean(self):
        if self.minimum > self.maximum:
            raise ValidationError('Minimum cannot be higher than maximum.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super(IngredientGroup, self).save(*args, **kwargs)

    @staticmethod
    def check_ingredients(ingredients, food):
        """
        Check whether the given ingredients can be made into an OrderedFood
        based on the closest food.
        """

        ingredientgroups = {}
        for ingredient in ingredients:
            group = ingredient.group
            amount = 1
            if group.id in ingredientgroups:
                amount += ingredientgroups[group.id]
            if group.maximum > 0 and amount > group.maximum:
                raise IngredientGroupMaxExceeded()
            ingredientgroups[group.id] = amount

        foodtype_groups = food.foodtype.ingredientgroup_set.all()

        for ingredientgroup in ingredientgroups:
            for foodtype_group in foodtype_groups:
                if foodtype_group.id == ingredientgroup:
                    break
            else:
                raise LinkingError()

        original_ingredients = food.ingredients.all()

        for ingredient in original_ingredients:
            group = ingredient.group
            if group.minimum > 0:
                in_groups = group.id in ingredientgroups
                if not in_groups:
                    raise IngredientGroupsMinimumNotMet()
                amount = ingredientgroups[group.id]

                if amount < group.minimum:
                    raise IngredientGroupsMinimumNotMet()

    @cached_property
    def ingredients(self):
        return self.ingredient_set.all()

    def __unicode__(self):
        return self.name


class Ingredient(models.Model, DirtyFieldsMixin):
    name = models.CharField(
        max_length=255
    )
    cost = models.DecimalField(
        default=0,
        max_digits=7,
        decimal_places=2
    )

    group = models.ForeignKey(
        IngredientGroup,
        on_delete=models.CASCADE
    )
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE
    )

    last_modified = models.DateTimeField(
        auto_now=True
    )

    def save(self, *args, **kwargs):
        if self.store != self.group.store:
            raise LinkingError()

        dirty_fields = self.get_dirty_fields(check_relationship=True)
        if 'group' in dirty_fields:
            for food in self.food_set.all():
                food.update_typical()

        super(Ingredient, self).save(*args, **kwargs)

    def __unicode__(self):
        return '#{id} {name} ({group})'.format(
            id=self.id,
            name=self.name,
            group=self.group
        )


class FoodCategory(models.Model):
    name = models.CharField(
        max_length=255
    )
    priority = models.PositiveIntegerField(
        default=0
    )
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name_plural = 'Food categories'
        unique_together = ('name', 'store',)

    def __unicode__(self):
        return self.name


class Quantity(models.Model):
    foodtype = models.ForeignKey(
        FoodType,
        on_delete=models.CASCADE
    )
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE
    )

    min = models.DecimalField(
        decimal_places=3,
        max_digits=7,
        default=1
    )
    max = models.DecimalField(
        decimal_places=3,
        max_digits=7,
        default=10
    )

    last_modified = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        unique_together = ('foodtype', 'store',)
        verbose_name_plural = 'Quantities'

    def clean(self):
        if self.min > self.max:
            raise ValidationError('Amount maximum need to be greater or equal to its minimum.')
        if not self.foodtype.is_valid_amount(self.min) or \
                not self.foodtype.is_valid_amount(self.max):
            raise InvalidFoodTypeAmount()

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Quantity, self).save(*args, **kwargs)

    def __unicode__(self):
        return '{min}-{max}'.format(
            min=self.min,
            max=self.max
        )


class Food(models.Model):
    name = models.CharField(
        max_length=255
    )
    description = models.TextField(
        blank=True
    )
    amount = models.DecimalField(
        decimal_places=3,
        max_digits=7,
        default=1
    )
    cost = models.DecimalField(
        decimal_places=2,
        max_digits=7
    )
    foodtype = models.ForeignKey(
        FoodType,
        on_delete=models.CASCADE
    )
    preorder_days = models.PositiveIntegerField(
        default=0
    )
    commentable = models.BooleanField(
        default=False
    )
    priority = models.BigIntegerField(
        default=0
    )

    category = models.ForeignKey(
        FoodCategory,
        on_delete=models.CASCADE
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRelation',
        blank=True
    )
    ingredientgroups = models.ManyToManyField(
        IngredientGroup,
        blank=True
    )
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE
    )

    last_modified = models.DateTimeField(
        auto_now=True
    )
    deleted = models.BooleanField(
        default=False
    )
    objects = FoodManager()

    class Meta:
        verbose_name_plural = 'Food'

    @cached_property
    def has_ingredients(self):
        return self.ingredients.count() > 0 and self.ingredientgroups.count() > 0

    @cached_property
    def quantity(self):
        try:
            return Quantity.objects.get(
                foodtype_id=self.foodtype_id,
                store_id=self.store_id
            )
        except Quantity.DoesNotExist:
            return None

    def update_typical(self):
        ingredientgroups = self.ingredientgroups.all()
        ingredientrelations = self.ingredientrelation_set.select_related(
            'ingredient__group'
        ).all()

        for ingredientrelation in ingredientrelations:
            ingredient = ingredientrelation.ingredient
            if ingredient.group not in ingredientgroups:
                if not ingredientrelation.typical:
                    ingredientrelation.typical = True
                    ingredientrelation.save()
            elif ingredientrelation.typical:
                ingredientrelation.typical = False
                ingredientrelation.save()

    def is_orderable(self, pickup, now=None):
        """
        Check whether this food can be ordered for the given day.
        This does not check whether the Store.wait has been exceeded!
        """
        if self.preorder_days == 0:
            return True
        else:
            now = datetime.now() if now is None else now
            # Amount of days needed to order in advance
            # (add 1 if it isn't before the preorder_time)
            preorder_days = self.preorder_days + (
                1 if now.time() > self.store.preorder_time else 0
            )

            # Calculate the amount of days between pickup and now
            difference_day = (pickup - now).days
            difference_day += (
                1
                if pickup.time() < now.time() and
                (now + (pickup - now)).day != now.day
                else 0
            )

            return difference_day >= preorder_days

    def is_valid_amount(self, amount):
        return amount > 0 and (
            float(amount).is_integer() or
            self.foodtype.inputtype != INPUT_SI_VARIABLE
        ) and (
            self.quantity is None or
            self.quantity.min <= amount <= self.quantity.max
        )

    def save(self, *args, **kwargs):
        if not self.foodtype.is_valid_amount(self.amount):
            raise InvalidFoodTypeAmount()
        if self.category.store_id != self.store_id:
            raise LinkingError()

        super(Food, self).save(*args, **kwargs)

        if self.deleted:
            self.delete()

    def delete(self, *args, **kwargs):
        if self.orderedfood_set.exclude(order__status__in=ORDER_STATUSES_ENDED).count() == 0:
            super(Food, self).delete(*args, **kwargs)
        elif not self.deleted:
            self.deleted = True
            self.save()

    def __unicode__(self):
        return self.name

    @staticmethod
    def changed_ingredients(sender, instance, action, reverse, model, pk_set, using, **kwargs):
        if len(action) > 4 and action[:4] == 'post':
            if isinstance(instance, Food):
                instance.update_typical()
            elif instance.__class__ in [Ingredient, IngredientGroup]:
                for food in instance.food_set.all():
                    food.update_typical()

    @classmethod
    def from_excel(cls, store, file):
        workbook = load_workbook(
            filename=file,
            read_only=True
        )

        if 'Food' not in workbook:
            raise ValidationError(
                _('The worksheet "Food" could not be found. Please use our template.')
            )

        worksheet = workbook['Food']
        mapping = [
            {
                'field_name': 'name',
            },
            {
                'field_name': 'description',
            },
            {
                'field_name': 'category',
                'instance': {
                    'model': FoodCategory,
                    'create': True,
                    'field_name': 'name'
                }
            },
            {
                'field_name': 'cost',
            },
            {
                'field_name': 'foodtype',
                'instance': {
                    'model': FoodType,
                    'field_name': 'name',
                    'store': False
                }
            },
            {
                'field_name': 'preorder_days',
            },
            {
                'field_name': 'priority',
            },
        ]
        mapping_length = len(mapping)

        food_list = []
        created_relations = []
        skip = True
        for row in worksheet.rows:
            # Skip headers
            if skip:
                skip = False
                continue

            kwargs = {}
            exclude = []

            for cell in row:
                if not isinstance(cell.column, int):
                    continue

                i = cell.column - 1
                if i >= mapping_length:
                    continue
                info = mapping[i]
                value = cell.value
                if 'instance' in info:
                    instance = info['instance']
                    create = instance.get('create', False)
                    model = instance['model']

                    exclude.append(info['field_name'])
                    where = {
                        instance['field_name']: cell.value
                    }
                    if instance.get('store', True):
                        where['store'] = store

                    if create:
                        value, created = model.objects.get_or_create(
                            **where
                        )
                        if created:
                            created_relations.append(value)
                    else:
                        value = model.objects.get(
                            **where
                        )

                kwargs[info['field_name']] = value

            food = Food(
                store=store,
                **kwargs
            )
            try:
                food.clean_fields(exclude=exclude)
            except ValidationError:
                for relation in created_relations:
                    relation.delete()
                raise ValidationError(
                    _('Could not import row %(row)d.') % {
                        'row': cell.row
                    }
                )

            food_list.append(food)

        try:
            cls.objects.bulk_create(food_list)
        except DatabaseError:
            for relation in created_relations:
                relation.delete()


class IngredientRelation(models.Model, DirtyFieldsMixin):
    food = models.ForeignKey(
        Food,
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE
    )
    selected = models.BooleanField(
        default=False
    )
    typical = models.BooleanField(
        default=False
    )

    class Meta:
        unique_together = ('food', 'ingredient',)

    def save(self, *args, **kwargs):
        if self.food.store_id != self.ingredient.store_id:
            raise LinkingError()

        dirty_fields = self.get_dirty_fields(check_relationship=True)
        if 'ingredient' in dirty_fields:
            self.food.update_typical()

        super(IngredientRelation, self).save(*args, **kwargs)

    def __unicode__(self):
        return unicode(self.ingredient)


class BaseTokenManager(DeviceManager):

    def create_token(self, arguments, defaults, clone=False):
        identifier_raw = random_token()
        defaults['identifier'] = identifier_raw

        try:
            token, created = self.update_or_create(
                defaults=defaults,
                **arguments
            )
        except MultipleObjectsReturned:
            self.filter(**arguments).delete()
            token, created = self.update_or_create(
                defaults=defaults,
                **arguments
            )

        if clone:
            token_copy = copy.copy(token)
            token_copy.identifier = identifier_raw
            return (token_copy, created,)
        return (token, created,)


class BaseToken(BareDevice, DirtyFieldsMixin):
    device = models.CharField(
        max_length=255
    )
    identifier = models.CharField(
        max_length=255
    )

    objects = BaseTokenManager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        # forced hashing can be removed when resetting migrations
        force_hashing = kwargs.pop('force_hashing', False)

        if self.pk is None or self.is_dirty() or force_hashing:
            identifier_dirty = self.get_dirty_fields().get('identifier', None)

            if self.pk is None or identifier_dirty is not None or force_hashing:
                self.identifier = make_password(self.identifier, hasher='sha1')

        super(BaseToken, self).save(*args, **kwargs)

    def check_identifier(self, identifier_raw):
        return check_password(identifier_raw, self.identifier)

    def __unicode__(self):
        return self.device


m2m_changed.connect(Food.changed_ingredients, sender=Food.ingredientgroups.through)
m2m_changed.connect(Food.changed_ingredients, sender=Food.ingredients.through)
