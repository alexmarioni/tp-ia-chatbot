import 'dart:convert';
import 'package:http/http.dart' as http;

class ChatService {
  // Cambiá según dónde corrés el backend:
  //   Emulador Android  → http://10.0.2.2:8000
  //   Dispositivo físico → http://<IP_DE_TU_PC>:8000
  //   Web / Desktop     → http://localhost:8000
  static const String _baseUrl = 'http://localhost:8000';

  Future<Map<String, dynamic>> sendMessage(
      String sessionId, String message) async {
    final response = await http
        .post(
          Uri.parse('$_baseUrl/chat'),
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode({'session_id': sessionId, 'message': message}),
        )
        .timeout(const Duration(seconds: 15));

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else if (response.statusCode == 410) {
      return {'reply': 'Esta sesión ya fue cerrada.', 'intent': 'closed', 'session_active': false};
    }
    throw Exception('Error del servidor: ${response.statusCode}');
  }

  Future<Map<String, dynamic>> sendCoords(
      String sessionId, double lat, double lon) async {
    final response = await http
        .post(
          Uri.parse('$_baseUrl/weather/coords'),
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode({'session_id': sessionId, 'lat': lat, 'lon': lon}),
        )
        .timeout(const Duration(seconds: 15));

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else if (response.statusCode == 410) {
      return {'reply': 'Esta sesión ya fue cerrada.', 'intent': 'closed', 'session_active': false};
    }
    throw Exception('Error del servidor: ${response.statusCode}');
  }

  Future<void> closeSession(String sessionId) async {
    await http
        .delete(Uri.parse('$_baseUrl/session/$sessionId'))
        .timeout(const Duration(seconds: 5));
  }
}
