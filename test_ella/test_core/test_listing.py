# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from django.test import TestCase

from nose import tools

from ella.core.models import Listing, Category

from test_ella.test_core import create_basic_categories, create_and_place_a_publishable, \
        create_and_place_more_publishables, list_all_publishables_in_category_by_hour

class TestListing(TestCase):

    def setUp(self):
        super(TestListing, self).setUp()
        create_basic_categories(self)
        create_and_place_a_publishable(self)
        create_and_place_more_publishables(self)
        list_all_publishables_in_category_by_hour(self)

    def test_get_listing_empty(self):
        c = Category.objects.create(
            title=u"third nested category",
            description=u"category nested in case.category_nested_second",
            tree_parent=self.category_nested_second,
            site_id = self.site_id,
            slug=u"third-nested-category",
        )

        l = Listing.objects.get_listing(category=c)
        tools.assert_equals(0, len(l))

    def test_get_listing_with_immediate_children(self):
        l = Listing.objects.get_listing(category=self.category, children=Listing.objects.IMMEDIATE)
        expected = [listing for listing in self.listings if listing.category in (self.category, self.category_nested)]
        tools.assert_equals(expected, l)

    def test_get_listing_with_immediate_children_no_duplicates(self):
        expected = [listing for listing in self.listings if listing.category in (self.category, self.category_nested)]

        listing = Listing.objects.create(
                publishable=expected[0].publishable,
                category=expected[0].category,
                publish_from=datetime.now() - timedelta(days=2),
            )
        expected[0] = listing
        l = Listing.objects.get_listing(category=self.category, children=Listing.objects.IMMEDIATE)
        tools.assert_equals(expected, l)

    def test_get_listing_with_all_children_no_duplicates(self):
        listing = Listing.objects.create(
                publishable=self.publishables[0],
                category=self.category_nested_second,
                publish_from=datetime.now() - timedelta(days=2),
            )

        l = Listing.objects.get_listing(category=self.category, children=Listing.objects.ALL)
        tools.assert_equals(len(self.listings), len(l))
        tools.assert_equals(listing, l[0])

    def test_get_listing_with_all_children(self):
        l = Listing.objects.get_listing(category=self.category, children=Listing.objects.ALL)
        tools.assert_equals(self.listings, list(l))

    def test_inactive_istings_wont_show(self):
        l = self.listings[0]
        l.publish_to = datetime.now() - timedelta(days=1)
        l.save()

        l = Listing.objects.get_listing(category=self.category, children=Listing.objects.ALL)

        tools.assert_equals(self.listings[1:], l)
