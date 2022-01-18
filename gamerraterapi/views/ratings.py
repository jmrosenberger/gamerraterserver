"""View module for handling requests about games"""
from django.core.exceptions import ValidationError
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from gamerraterapi.models import Player, Rating, Game
from django.contrib.auth import get_user_model


class RatingsView(ViewSet):
    """Level up games"""

    def create(self, request):
        """Handle POST operations
        Returns:
            Response -- JSON serialized game instance
        """

        # Uses the token passed in the `Authorization` header
        player = Player.objects.get(user=request.auth.user)

        # Try to save the new game to the database, then
        # serialize the game instance as JSON, and send the
        # JSON as a response to the client request
        try:
            # Create a new Python instance of the Game class
            # and set its properties from what was sent in the
            # body of the request from the client.
            rating = Rating.objects.create(
                rating=request.data["rating"],
                game=Game.objects.get(pk=request.data["gameId"]),
                player=player
            )
            serializer = RatingSerializer(rating, context={'request': request})

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # If anything went wrong, catch the exception and
        # send a response with a 400 status code to tell the
        # client that something was wrong with its request data
        except ValidationError as ex:
            return Response({"reason": ex.message}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single game
        Returns:
            Response -- JSON serialized game instance
        """
        try:
            rating = Rating.objects.get(pk=pk)
            serializer = RatingSerializer(rating, context={'request': request})
            return Response(serializer.data)
        except Exception as ex:
            return HttpResponseServerError(ex)

    def update(self, request, pk=None):
        """Handle PUT requests for a game
        Returns:
            Response -- Empty body with 204 status code
        """
        player = Player.objects.get(user=request.auth.user)

        # Do mostly the same thing as POST, but instead of
        # creating a new instance of Game, get the game record
        # from the database whose primary key is `pk`
        rating = Rating.objects.get(pk=pk)
        rating.rating = request.data["rating"]

        rating.save()

        # 204 status code means everything worked but the
        # server is not sending back any data in the response
        return Response({}, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None):
        """Handle DELETE requests for a single game
        Returns:
            Response -- 200, 404, or 500 status code
        """
        try:
            rating = Rating.objects.get(pk=pk)
            rating.delete()

            return Response({}, status=status.HTTP_204_NO_CONTENT)

        except Rating.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request):
        """Handle GET requests to games resource
        Returns:
            Response -- JSON serialized list of games
        """
        ratings = Rating.objects.all()

        game = self.request.query_params.get('gameId', None)
        if game is not None:
            ratings = ratings.filter(game_id__id=game)
        serializer = RatingSerializer(
            ratings, many=True, context={'request': request})
        return Response(serializer.data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name']


class PlayerSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False)

    class Meta:
        model = Player
        fields = ['user']

class GameSerializer(serializers.ModelSerializer):
    """JSON serializer for games
    Arguments:
        serializer type
    """

    class Meta:
        model = Game
        fields = ('id', 'title', 'description', 'designer',
                  'year_released', 'num_players', 'gameplay_length', 'age')
        depth = 1

class RatingSerializer(serializers.ModelSerializer):
    """JSON serializer for games
    Arguments:
        serializer type
    """
    player = PlayerSerializer(many=False)
    game = GameSerializer(many=False)

    class Meta:
        model = Rating
        fields = ('id', 'rating', 'game',
                  'player')
        depth = 1