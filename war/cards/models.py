from django.contrib.auth.models import AbstractUser
from django.db import models


class Card(models.Model):
    SPADE = 0
    CLUB = 1
    DIAMOND = 2
    HEART = 3
    SUITS = (
        (SPADE, "spade"),
        (CLUB, "club"),
        (DIAMOND, "diamond"),
        (HEART, "heart")
    )
    suit = models.PositiveSmallIntegerField(choices=SUITS)
    rank = models.CharField(max_length=5)
    image = models.ImageField(upload_to='card_images', blank=True, null=True)

    def get_ranking(self):
        rankings = {
            'two': 2,
            'three': 3,
            'four': 4,
            'five': 5,
            'six': 6,
            'seven': 7,
            'eight': 8,
            'nine': 9,
            'ten': 10,
            'jack': 11,
            'queen': 12,
            'king': 13,
            'ace': 14
        }
        return rankings[self.rank]

    def get_war_result(self, card_to_check):
        my_ranking = self.get_ranking()
        card_to_check_ranking = card_to_check.get_ranking()

        print my_ranking, card_to_check_ranking

        if my_ranking > card_to_check_ranking:
            return 1
        elif my_ranking == card_to_check_ranking:
            return 0
        else:
            return -1

    def __unicode__(self):
        return u"{} of {}s".format(self.rank, self.get_suit_display())


class Player(AbstractUser):
    phone = models.CharField(max_length=12, help_text="Format should be: 650-111-2222")


class WarGame(models.Model):
    LOSS = -1
    TIE = 0
    WIN = 1
    RESULTS = (
        (LOSS, "loss"),
        (TIE, "tie"),
        (WIN, "win")
    )

    result = models.IntegerField(choices=RESULTS)
    player = models.ForeignKey(Player)
