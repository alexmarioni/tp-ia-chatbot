import 'package:flutter_test/flutter_test.dart';
import 'package:chatbot_clima/main.dart';

void main() {
  testWidgets('App arranca sin errores', (WidgetTester tester) async {
    await tester.pumpWidget(const ChatbotApp());
    expect(find.text('Chatbot de Clima'), findsOneWidget);
  });
}
