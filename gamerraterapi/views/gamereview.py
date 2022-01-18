"""View module for handling requests about games"""
from django.core.exceptions import ValidationError
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from gamerraterapi.models import Player, Review
from django.contrib.auth import get_user_model


class GameReviewView(ViewSet):
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
            review = Review.objects.create(
                review=request.data["review"],
                date=request.data["date"],
                game_id=request.data["gameId"],
                player=player,
            )
            serializer = ReviewSerializer(review, context={'request': request})

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
            review = Review.objects.get(pk=pk)
            serializer = ReviewSerializer(review, context={'request': request})
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
        review = Review.objects.get(pk=pk)
        review.review = request.data["review"]
        review.date = request.data["date"]

        review.save()

        # 204 status code means everything worked but the
        # server is not sending back any data in the response
        return Response({}, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None):
        """Handle DELETE requests for a single game
        Returns:
            Response -- 200, 404, or 500 status code
        """
        try:
            review = Review.objects.get(pk=pk)
            review.delete()

            return Response({}, status=status.HTTP_204_NO_CONTENT)

        except Review.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request):
        """Handle GET requests to games resource
        Returns:
            Response -- JSON serialized list of games
        """
        reviews = Review.objects.all()

        # http://localhost:8000/reviews?gameId=1
        game = self.request.query_params.get('gameId', None)
        if game is not None:
            reviews = reviews.filter(game_id__id=game)
        serializer = ReviewSerializer(
            reviews, many=True, context={'request': request})
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


class ReviewSerializer(serializers.ModelSerializer):
    """JSON serializer for games
    Arguments:
        serializer type
    """
    player = PlayerSerializer(many=False)

    class Meta:
        model = Review
        fields = ('id', 'review', 'date', 'game',
                  'player')
        depth = 1