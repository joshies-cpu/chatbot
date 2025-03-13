from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import requests
from langdetect import detect, LangDetectException

# Import database functions
from database import (
    init_db, add_to_cart, remove_from_cart, view_cart, clear_cart,
    add_user_preference, get_user_preferences, add_purchase, get_purchase_history
)

# FastAPI endpoint URLs
BASE_URL = "http://localhost:8000"

# Initialize database when the action server starts
init_db()

class ActionDetectLanguage(Action):
    def name(self) -> Text:
        return "action_detect_language"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        message = tracker.latest_message.get('text', '')
        
        try:
            detected_lang = detect(message) if message else "en"
        except LangDetectException:
            detected_lang = "en"

        return [SlotSet("language", detected_lang)]

class ActionSearchProduct(Action):
    def name(self) -> Text:
        return "action_search_product"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        category = tracker.get_slot("category")
        brand = tracker.get_slot("brand")
        max_price = tracker.get_slot("max_price")
        min_price = tracker.get_slot("min_price")
        sort_by = tracker.get_slot("sort_by")
        user_id = tracker.sender_id

        params = {"user_id": user_id, "category": category, "brand": brand, "max_price": max_price, "min_price": min_price, "sort_by": sort_by}
        params = {k: v for k, v in params.items() if v is not None}

        try:
            response = requests.get(f"{BASE_URL}/search", params=params, timeout=5)
            response.raise_for_status()
            data = response.json()

            products = data.get("products", [])
            if not products:
                dispatcher.utter_message(text="No products found matching your criteria.")
                return [SlotSet("search_results", [])]

            result_message = "Here are the products I found:\n"
            for i, product in enumerate(products[:5], 1):
                result_message += f"{i}. {product['name']} - ${product['price']} ({product['brand']})\n"

            dispatcher.utter_message(text=result_message)
            return [SlotSet("search_results", products if products else [])]
        except requests.RequestException:
            dispatcher.utter_message(text="I couldn't connect to the product search service. Please try again later.")
        except Exception:
            dispatcher.utter_message(text="An error occurred while searching for products. Please try again.")

        return [SlotSet("search_results", [])]

class ActionProcessPayment(Action):
    def name(self) -> Text:
        return "action_process_payment"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        payment_method = tracker.get_slot("payment_method")
        if not payment_method:
            dispatcher.utter_message(text="Please specify a valid payment method.")
            return []

        dispatcher.utter_message(text=f"Processing your payment using {payment_method}...")
        dispatcher.utter_message(text="Payment successful! Your order has been confirmed.")
        return []

class ActionHandlePaymentFailure(Action):
    def name(self) -> Text:
        return "action_handle_payment_failure"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="It looks like your payment failed. Please check your payment method and try again.")
        dispatcher.utter_message(text="If the issue persists, contact customer support.")
        return []
class ActionViewCart(Action):
    def name(self) -> Text:
        return "action_view_cart"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_id = tracker.sender_id
        
        try:
            cart_items = view_cart(user_id)  # Assuming `view_cart` fetches cart details from the database
            
            if not cart_items:
                dispatcher.utter_message(text="Your cart is empty.")
                return [SlotSet("cart_items", [])]

            cart_message = "Items in your cart:\n" + "\n".join(f"{i+1}. {item}" for i, item in enumerate(cart_items))
            
            dispatcher.utter_message(text=cart_message)
            return [SlotSet("cart_items", cart_items if cart_items else [])]
        except Exception:
            dispatcher.utter_message(text="Error viewing cart. Please try again.")
            return [SlotSet("cart_items", [])]
class ActionAskDiscounts(Action):
    def name(self) -> Text:
        return "action_ask_discounts"

    def run(self, dispatcher: CollectingDispatcher, 
            tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="We currently have discounts on select items. Check out our deals section.")
        return []
