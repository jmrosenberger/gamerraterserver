"""View module for handling requests about games"""
from django.core.exceptions import ValidationError
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from gamerraterapi.models import Game, Player, Category
from gamerraterapi.views.category import CategorySerializer
# from django.db.models import Q

class GameView(ViewSet):
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
            game = Game.objects.create(
                title=request.data["title"],
                description=request.data["description"],
                designer=request.data["designer"],
                year_released=request.data["yearReleased"],
                num_players=request.data["numPlayers"],
                gameplay_length=request.data["gameplayLength"],
                age=request.data["age"]
            )
            game.categories.set(request.data["categories"])
            serializer = GameSerializer(game, context={'request': request})

            return Response(serializer.data, status.HTTP_201_CREATED)

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
            # `pk` is a parameter to this function, and
            # Django parses it from the URL route parameter
            #   http://localhost:8000/games/2
            #
            # The `2` at the end of the route becomes `pk`
            game = Game.objects.get(pk=pk)
            serializer = GameSerializer(game, context={'request': request})
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
        game = Game.objects.get(pk=pk)
        game.title = request.data["title"]
        game.description = request.data["description"]
        game.designer = request.data["designer"]
        game.year_released = request.data["yearReleased"]
        game.num_players = request.data["numPlayers"]
        game.gameplay_length = request.data["gameplayLength"]
        game.age = request.data["age"]
        game.categories.set(request.data["categories"])

        game.save()

        # 204 status code means everything worked but the
        # server is not sending back any data in the response
        return Response({}, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None):
        """Handle DELETE requests for a single game
        Returns:
            Response -- 200, 404, or 500 status code
        """
        try:
            game = Game.objects.get(pk=pk)
            game.delete()

            return Response({}, status=status.HTTP_204_NO_CONTENT)

        except Game.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request):
        """Handle GET requests to games resource
        Returns:
            Response -- JSON serialized list of games
        """
        
        player = Player.objects.get(user=request.auth.user)
        # Get all game records from the database
        games = Game.objects.all()

        # search_text = self.request.query_params.get('q', None)
        # order_by_prop = self.request.query_params.get('orderby', None)

        # if search_text is not None:
        #     games = Game.objects.filter(
        #         Q(title__contains=search_text) |
        #         Q(description__contains=search_text) |
        #         Q(designer__contains=search_text)
        #     )

        # if order_by_prop is not None:
        #     games = Game.objects.order_by(order_by_prop)
        serializer = GameSerializer(
            games, many=True, context={'request': request})
        
        return Response(serializer.data)


class GameSerializer(serializers.ModelSerializer):
    """JSON serializer for games
    Arguments:
        serializer type
    """
    # categories = CategorySerializer(many=True)
    
    class Meta:
        model = Game
        fields = ('id', 'title', 'description', 'designer',
                  'year_released', 'num_players', 'gameplay_length', 'age', 'categories', 'average_rating')
        depth = 1