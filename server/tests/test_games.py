import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import patch, MagicMock
import json
from app import app

class TestGamesRoutes(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        app.config['TESTING'] = True

        # Common test data
        self.test_games = [
            {
                'id': 1, 
                'title': "Pipeline Panic", 
                'description': "Build your DevOps pipeline before chaos ensues",
                'publisher_name': "DevGames Inc", 
                'category_name': "Strategy", 
                'star_rating': 4.5
            },
            {
                'id': 2, 
                'title': "Agile Adventures", 
                'description': "Navigate your team through sprints and releases",
                'publisher_name': "Scrum Masters", 
                'category_name': "Card Game", 
                'star_rating': 4.2
            }
        ]

    def _create_mock_game(self, title, description, id=None, publisher_name=None, category_name=None, star_rating=None):
        """Create a mock game with standard attributes"""
        game = MagicMock(spec=['to_dict', 'id', 'title', 'description'])
        game.id = id
        game.title = title
        game.description = description
        
        game_dict = {
            'id': id, 
            'title': title, 
            'description': description,
            'star_rating': star_rating,
            'publisher': {'id': id, 'name': publisher_name} if publisher_name else None,
            'category': {'id': id, 'name': category_name} if category_name else None
        }
            
        game.to_dict.return_value = game_dict
        return game
        
    def _setup_mock_query(self, mock_query, games):
        """Configure the query mock with chainable methods"""
        query_mock = MagicMock()
        mock_query.return_value = query_mock
        
        # Setup all chainable methods to return self
        for method in ['join', 'filter', 'all', 'first']:
            getattr(query_mock, method).return_value = query_mock
        
        # Set actual return values
        query_mock.all.return_value = games
        query_mock.first.return_value = games[0] if games else None
        
        return query_mock
        
    def _assert_game_data(self, game_data, expected_game):
        """Assert that game data matches expected values"""
        self.assertEqual(game_data['id'], expected_game['id'])
        self.assertEqual(game_data['title'], expected_game['title'])
        self.assertEqual(game_data['description'], expected_game['description'])
        
        if 'publisher_name' in expected_game and expected_game['publisher_name']:
            self.assertEqual(game_data['publisher']['name'], expected_game['publisher_name'])
            
        if 'category_name' in expected_game and expected_game['category_name']:
            self.assertEqual(game_data['category']['name'], expected_game['category_name'])
            
        if 'star_rating' in expected_game:
            self.assertEqual(game_data['star_rating'], expected_game['star_rating'])

    @patch('routes.games.get_games_base_query')
    def test_get_games_success(self, mock_query):
        """Test successful retrieval of multiple games"""
        # Arrange
        mock_games = [
            self._create_mock_game(**self.test_games[0]),
            self._create_mock_game(**self.test_games[1])
        ]
        mock_query.return_value.all.return_value = mock_games
        
        # Act
        response = self.app.get('/api/games')
        data = json.loads(response.data)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 2)
        
        self._assert_game_data(data[0], self.test_games[0])
        self._assert_game_data(data[1], self.test_games[1])
        mock_query.assert_called_once()
        
    @patch('routes.games.get_games_base_query')
    def test_get_games_empty(self, mock_query):
        """Test retrieval when no games are available"""
        # Arrange
        mock_query.return_value.all.return_value = []
        
        # Act
        response = self.app.get('/api/games')
        data = json.loads(response.data)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, [])

    @patch('routes.games.get_games_base_query')
    def test_get_games_structure(self, mock_query):
        """Test the response structure for a single game"""
        # Arrange
        game = self._create_mock_game(**self.test_games[0])
        mock_query.return_value.all.return_value = [game]
        
        # Act
        response = self.app.get('/api/games')
        data = json.loads(response.data)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        
        required_fields = ['id', 'title', 'description', 'publisher', 'category', 'star_rating']
        for field in required_fields:
            self.assertIn(field, data[0])

    @patch('routes.games.get_games_base_query')
    def test_get_game_by_id_success(self, mock_query):
        """Test successful retrieval of a single game by ID"""
        # Arrange
        game = self._create_mock_game(**self.test_games[0])
        mock_query.return_value.filter.return_value.first.return_value = game
        
        # Act
        response = self.app.get('/api/games/1')
        data = json.loads(response.data)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self._assert_game_data(data, self.test_games[0])
        
    @patch('routes.games.get_games_base_query')
    def test_get_game_by_id_not_found(self, mock_query):
        """Test retrieval of a non-existent game by ID"""
        # Arrange
        mock_query.return_value.filter.return_value.first.return_value = None
        
        # Act
        response = self.app.get('/api/games/999')
        data = json.loads(response.data)
        
        # Assert
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['error'], "Game not found")


if __name__ == '__main__':
    unittest.main()
