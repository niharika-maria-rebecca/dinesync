from flask import Blueprint, request, jsonify, session
from models.dish import Dish
import random

chatbot_bp = Blueprint('chatbot', __name__)

def get_available_dishes():
    return Dish.query.filter_by(is_available=True).all()

def get_by_category(category):
    return Dish.query.filter_by(category=category, is_available=True).all()

def get_specials():
    return Dish.query.filter_by(is_todays_special=True, is_available=True).all()

@chatbot_bp.route('/chat', methods=['POST'])
def chat():
    try:
        data         = request.get_json()
        user_message = data.get('message', '').strip().lower()
        customer_name= session.get('customer_name', 'Guest')
        if not user_message:
            return jsonify({'error': 'Empty message'}), 400
        reply = generate_reply(user_message, customer_name)
        return jsonify({'reply': reply, 'success': True})
    except Exception as e:
        print(f"Chat error: {e}")
        return jsonify({'reply': 'Hi! Ask me about our menu — specials, spicy food, drinks and more!', 'success': True})


def generate_reply(msg, name):
    dishes   = get_available_dishes()
    specials = get_specials()

    # ── Greetings ──
    if any(w in msg for w in ['hi','hello','hey','hii','helo','hai','good morning','good evening','good afternoon','sup','whats up']):
        return f"Hi {name}! 👋 Welcome to DineSync! I am DineBot, your personal food assistant. You can ask me about:\n🌶️ Spicy dishes\n🥗 Vegetarian options\n⭐ Today's specials\n🥤 Drinks\n🍮 Desserts\n💰 Budget options\n⏱️ Quick meals"

    # ── How are you ──
    if any(w in msg for w in ['how are you','how r you','whats up','wassup']):
        return f"I am doing great {name}! 😊 Ready to help you find the perfect dish. What are you in the mood for today?"

    # ── What can you do ──
    if any(w in msg for w in ['what can you do','help','what do you know','capabilities','how can you help']):
        return f"I can help you with:\n⭐ Today's specials\n🌶️ Spicy dish recommendations\n🥗 Vegetarian options\n🍗 Non-veg dishes\n🥤 Drink suggestions\n🍮 Dessert options\n💰 Budget-friendly picks\n⏱️ Quickest dishes\nJust ask me anything about the menu!"

    # ── Today's specials ──
    if any(w in msg for w in ['special','today','recommend','best','suggested','chef','popular','must try','must have']):
        if specials:
            names = ', '.join([f"{d.name} (₹{d.price})" for d in specials])
            return f"⭐ Today's specials are: {names}!\nThese are our chef's top picks — freshly prepared and highly recommended. Want to know more about any of these?"
        return "We don't have any specials today, but our entire menu is fresh and delicious! Want me to suggest something specific?"

    # ── Spicy ──
    if any(w in msg for w in ['spicy','hot','masala','pepper','chilli','chili','fire','burn']):
        spicy = [d for d in dishes if any(w in d.name.lower() or w in (d.description or '').lower()
                 for w in ['spicy','masala','pepper','chilli','65','tikka','kebab','tandoori'])]
        if spicy:
            d = random.choice(spicy)
            return f"🌶️ Perfect choice for spice lovers! Try our **{d.name}** for just ₹{d.price}!\n{d.description}\nReady in ~{d.prep_time} mins. Want anything else?"
        return "🌶️ Try Chicken 65 or Seekh Kebab from our Starters — both are packed with amazing spices!"

    # ── Vegetarian ──
    if any(w in msg for w in ['veg','vegetarian','no meat','paneer','vegan','pure veg','only veg']):
        veg = [d for d in dishes if any(w in d.name.lower() for w in
               ['paneer','veg','dal','aloo','gobi','spring roll','lassi','chai','gulab','ice','rasgulla','tomato','lime','water','coffee','mango'])]
        if veg:
            picks = random.sample(veg, min(3, len(veg)))
            names = '\n'.join([f"  • {d.name} — ₹{d.price}" for d in picks])
            return f"🥗 Great vegetarian options for you:\n{names}\nAll freshly prepared! Which one catches your eye?"
        return "We have great vegetarian options! Check Paneer Tikka, Paneer Butter Masala, Dal Tadka and Spring Rolls!"

    # ── Non veg ──
    if any(w in msg for w in ['chicken','non veg','nonveg','meat','fish','mutton','egg','biryani']):
        nonveg = [d for d in dishes if any(w in d.name.lower() for w in ['chicken','fish','seekh','kebab','biryani'])]
        if nonveg:
            picks = random.sample(nonveg, min(2, len(nonveg)))
            names = '\n'.join([f"  • {d.name} — ₹{d.price}" for d in picks])
            return f"🍗 Top non-veg picks:\n{names}\nBoth are crowd favourites! Want to add one to your cart?"
        return "Try Chicken Biryani, Chicken 65 or Fish Curry — all very popular!"

    # ── Starters ──
    if any(w in msg for w in ['starter','starters','appetizer','snack','light','begin','start']):
        starters = get_by_category('Starters')
        if starters:
            names = '\n'.join([f"  • {d.name} — ₹{d.price} (~{d.prep_time} mins)" for d in starters])
            return f"🥗 Our Starters:\n{names}\nPerfect to begin your meal!"
        return "Check our Starters section for great appetizers!"

    # ── Main course ──
    if any(w in msg for w in ['main','meal','food','hungry','rice','roti','naan','curry','lunch','dinner','full meal','heavy']):
        mains = get_by_category('Main Course')
        if mains:
            names = '\n'.join([f"  • {d.name} — ₹{d.price} (~{d.prep_time} mins)" for d in mains])
            return f"🍛 Our Main Course options:\n{names}\nAll filling and delicious!"
        return "Our Main Course has Biryani, Paneer dishes, Dal and more!"

    # ── Drinks ──
    if any(w in msg for w in ['drink','drinks','juice','water','lassi','chai','tea','coffee','thirsty','beverage','soda','cold']):
        drinks = get_by_category('Drinks')
        if drinks:
            names = '\n'.join([f"  • {d.name} — ₹{d.price} (~{d.prep_time} mins)" for d in drinks])
            return f"🥤 Our Drinks menu:\n{names}\nRefreshing options for you!"
        return "We have Mango Lassi, Masala Chai, Cold Coffee, Fresh Lime Soda and Mineral Water!"

    # ── Desserts ──
    if any(w in msg for w in ['sweet','dessert','desserts','ice cream','gulab','rasgulla','mithai','sugar']):
        desserts = get_by_category('Desserts')
        if desserts:
            names = '\n'.join([f"  • {d.name} — ₹{d.price} (~{d.prep_time} mins)" for d in desserts])
            return f"🍮 Our Desserts:\n{names}\nPerfect sweet ending to your meal!"
        return "Try Gulab Jamun, Ice Cream or Rasgulla for dessert!"

    # ── Full menu ──
    if any(w in msg for w in ['menu','all','full menu','show menu','what do you have','what is available','available']):
        categories = ['Starters', 'Main Course', 'Drinks', 'Desserts']
        reply = "🍽️ Here's what we have today:\n"
        for cat in categories:
            items = get_by_category(cat)
            if items:
                reply += f"\n{cat}:\n"
                for d in items:
                    reply += f"  • {d.name} — ₹{d.price}\n"
        return reply

    # ── Price / cheap / budget ──
    if any(w in msg for w in ['cheap','budget','affordable','less price','low price','inexpensive','cost','price']):
        cheap = sorted(dishes, key=lambda d: d.price)[:4]
        names = '\n'.join([f"  • {d.name} — ₹{d.price}" for d in cheap])
        return f"💰 Most affordable options:\n{names}\nGreat taste at great prices!"

    # ── Expensive / premium ──
    if any(w in msg for w in ['expensive','premium','best quality','special','luxury','treat']):
        expensive = sorted(dishes, key=lambda d: d.price, reverse=True)[:3]
        names = '\n'.join([f"  • {d.name} — ₹{d.price}" for d in expensive])
        return f"👑 Our premium dishes:\n{names}\nWorth every rupee — treat yourself!"

    # ── Quick / fast ──
    if any(w in msg for w in ['quick','fast','hurry','how long','wait','time','minutes','urgent','asap']):
        fast = sorted(dishes, key=lambda d: d.prep_time)[:3]
        names = '\n'.join([f"  • {d.name} (~{d.prep_time} mins)" for d in fast])
        return f"⏱️ Quickest items right now:\n{names}\nThese will be ready the fastest!"

    # ── Combo / pairing ──
    if any(w in msg for w in ['combo','pair','with','goes well','combination','suggest','along']):
        return "🍽️ Great combos:\n  • Chicken Biryani + Mango Lassi\n  • Paneer Butter Masala + Butter Naan\n  • Chicken 65 + Fresh Lime Soda\n  • Dal Tadka + Rice + Gulab Jamun\nWant me to add any of these to your cart?"

    # ── Thank you ──
    if any(w in msg for w in ['thank','thanks','ty','thank you','tq','ok','okay','got it','sure','great','awesome','nice','perfect']):
        return f"You're welcome {name}! 😊 Enjoy your meal at DineSync! Don't hesitate to ask if you need anything else. Bon appétit! 🍽️"

    # ── Bye ──
    if any(w in msg for w in ['bye','goodbye','see you','cya','take care']):
        return f"Goodbye {name}! 👋 Hope you enjoyed your meal at DineSync. Come back soon!"

    # ── Complaint / problem ──
    if any(w in msg for w in ['problem','issue','complaint','wrong','bad','not good','delay','late']):
        return "I'm sorry to hear that! 😔 Please press the 🔔 **Call Waiter** button on the left sidebar and our staff will assist you immediately!"

    # ── Waiter ──
    if any(w in msg for w in ['waiter','staff','help','assistance','person','human','someone']):
        return "To call a waiter, click the 🔔 **Call Waiter** button on the left sidebar! They will come to your table immediately."

    # ── Default — show random popular dishes ──
    picks = random.sample(dishes, min(3, len(dishes)))
    names = ', '.join([d.name for d in picks])
    return f"I am here to help! 😊 You can ask me about:\n🌶️ Spicy dishes  🥗 Veg options  ⭐ Specials\n🥤 Drinks  🍮 Desserts  💰 Budget picks  ⏱️ Quick meals\n\nCurrently popular: {names}"


@chatbot_bp.route('/chat/specials', methods=['GET'])
def get_specials_route():
    specials = Dish.query.filter_by(is_todays_special=True, is_available=True).all()
    return jsonify({'specials': [{'name': d.name, 'price': d.price} for d in specials]})