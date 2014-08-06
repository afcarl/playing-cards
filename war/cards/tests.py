from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from cards.forms import EmailUserCreationForm
from cards.models import Card, Player, WarGame
from cards.test_utils import run_pep8_for_package, run_pyflakes_for_package
from cards.utils import create_deck
from django.test import TestCase

__author__ = 'roxnairani'


class UtilTestCase(TestCase):
    def test_create_deck_count(self):
        """Test that we created 52 cards"""
        create_deck()
        self.assertEqual(Card.objects.count(), 52)


class ModelTestCase(TestCase):
    def test_get_ranking(self):
        """Test that we get the proper ranking for a card"""
        card = Card.objects.create(suit=Card.CLUB, rank="jack")
        self.assertEqual(card.get_ranking(), 11)

    def test_get_war_result_greater(self):
        """Tests greater than get_war_result function"""
        my_card = Card.objects.create(suit=Card.CLUB, rank="ten")
        card_to_check = Card.objects.create(suit=Card.CLUB, rank="six")
        self.assertEqual(my_card.get_war_result(card_to_check), 1)

    def test_get_war_result_equal(self):
        """Tests equality in get_war_result function"""
        my_card = Card.objects.create(suit=Card.CLUB, rank="ten")
        card_to_check = Card.objects.create(suit=Card.HEART, rank="ten")
        self.assertEqual(my_card.get_war_result(card_to_check), 0)

    def test_get_war_result_less(self):
        """Tests less than get_war_result function"""
        my_card = Card.objects.create(suit=Card.CLUB, rank="six")
        card_to_check = Card.objects.create(suit=Card.CLUB, rank="ten")
        self.assertEqual(my_card.get_war_result(card_to_check), -1)


class FormTestCase(TestCase):
    def test_clean_username_exception(self):
        # Create a player so that this username we're testing is already taken
        Player.objects.create_user(username='test-user')

        # set up the form for testing
        form = EmailUserCreationForm()
        form.cleaned_data = {'username': 'test-user'}

        # use a context manager to watch for the validation error being raised
        with self.assertRaises(ValidationError):
            form.clean_username()

    def test_clean_username(self):
        # set up the form for testing
        form = EmailUserCreationForm()
        form.cleaned_data = {'username': 'test-user'}

        self.assertEqual(form.cleaned_data['username'], 'test-user')


class ViewTestCase(TestCase):
    def setUp(self):
        create_deck()

    def create_war_game(self, user, result=WarGame.LOSS):
        WarGame.objects.create(result=result, player=user)

    def test_home_page(self):
        response = self.client.get(reverse('home'))
        self.assertIn('<p>Suit: spade, Rank: two</p>', response.content)
        self.assertEqual(response.context['cards'].count(), 52)

    # POST REQUEST
    def test_register_page(self):
        username = 'new-user'
        data = {
            'username': username,
            'email': 'test@test.com',
            'password1': 'test',
            'password2': 'test'
        }
        response = self.client.post(reverse('register'), data)

        # Check this user was created in the database
        self.assertTrue(Player.objects.filter(username=username).exists())

        # Check it's a redirect to the profile page
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertTrue(response.get('location').endswith(reverse('profile')))

    # GET REQUEST - NEEDS USER LOGGED IN
    def test_profile_page(self):
        # Create user and log them in
        password = 'passsword'
        user = Player.objects.create_user(username='test-user', email='test@test.com', password=password)
        self.client.login(username=user.username, password=password)

        # Set up some war game entries
        self.create_war_game(user)
        self.create_war_game(user, WarGame.WIN)

        # Make the url call and check the html and games queryset length
        response = self.client.get(reverse('profile'))
        self.assertInHTML('<p>Your email address is {}</p>'.format(user.email), response.content)
        self.assertEqual(len(response.context['games']), 2)

    # PRACTICE
    def test_faq_page(self):
        response = self.client.get(reverse('faq'))
        self.assertIn('<p>Q: Can I win real money on this website?</p>', response.content)

    def test_filters_page(self):
        response = self.client.get(reverse('filters'))
        self.assertIn('We have 52 cards', response.content)
        self.assertEqual(response.context['cards'].count(), 52)

    def test_poker_page(self):
        user = Player.objects.create_user(username='test-user', email='test@test.com', password='password')
        self.client.login(username=user.username, password=user.password)

        response = self.client.get(reverse('poker'))
        self.assertEqual(response.context['cards'].count(), 5)
        self.assertInHTML("<h2>Poker!</h2>", response.content)

    # ## NOT WORKING YET
    # def test_login_page(self):
    #     data = {
    #         'username': 'username',
    #         'password': 'password'
    #     }
    #     response = self.client.post(reverse('login'), data)
    #
    #     # Check it's a redirect to the profile page
    #     self.assertIsInstance(HttpResponseRedirect, response)
    #     # self.assertTrue(user.is_authenticated())
    #     self.assertTrue(response.get('location').endswith(reverse('profile')))

    # NOT WORKING YET
    # def test_war_page(self):
    #     user = Player.objects.create_user(username='test-user', email='test@test.com', password='password')
    #     self.client.login(username=user.username, password=user.password)
    #
    #     self.create_war_game(user)
    #
    #     response = self.client.get(reverse('war'))
    #     self.assertEqual(response.context['cards'].count(), 5)
    #     self.assertInHTML("<h2>War!</h2>", response.content)


class SyntaxTest(TestCase):
    def test_syntax(self):
        """
        Run pyflakes/pep8 across the code base to check for potential errors.
        """
        packages = ['cards']
        warnings = []
        # Eventually should use flake8 instead so we can ignore specific lines via a comment
        for package in packages:
            warnings.extend(run_pyflakes_for_package(package, extra_ignore=("_settings",)))
            warnings.extend(run_pep8_for_package(package, extra_ignore=("_settings",)))
        if warnings:
            self.fail("{0} Syntax warnings!\n\n{1}".format(len(warnings), "\n".join(warnings)))
