#!/usr/bin/env python3
"""Rewrite Food & Drink exercise passages as daily blog / speaking-style English.

Style matches IELTS/SPEAKING food pages: first-person, natural connectors,
vocab woven into a real story (not \"you notice X, Y, Z\" lists).
"""
from __future__ import annotations

import importlib.util
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "public" / "blog" / "english" / "food-drink"

# Import helpers from generator without running main()
_spec = importlib.util.spec_from_file_location(
    "gen_ex", Path(__file__).with_name("_gen_english_exercises.py")
)
_gen = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader
_spec.loader.exec_module(_gen)

TOPICS = _gen.TOPICS
collect_words = _gen.collect_words
mark_sentence = _gen.mark_sentence
verify_coverage = _gen.verify_coverage
wrap_exercise = _gen.wrap_exercise
esc = _gen.esc


# ---------------------------------------------------------------------------
# Handcrafted blog / speaking paragraphs: (en, vi)
# Every LanGeek form for that level must appear as a whole word in EN.
# ---------------------------------------------------------------------------

PASSAGES: dict[str, list[tuple[str, str]]] = {
    "A1": [
        (
            "I’m a big fan of simple food at home. Most days start with breakfast — "
            "maybe bread with butter and jam, or an egg with a little cheese. "
            "I drink tea or coffee, and sometimes chocolate milk if I want something sweet. "
            "A glass of cold milk works too when I’m in a hurry.",
            "Tôi rất thích đồ ăn đơn giản ở nhà. Hầu hết các ngày bắt đầu bằng breakfast — "
            "có thể là bread với butter và jam, hoặc egg với chút cheese. "
            "Tôi uống tea hoặc coffee, và đôi khi chocolate milk nếu muốn ngọt. "
            "Một ly milk lạnh cũng ổn khi tôi đang vội.",
        ),
        (
            "For lunch I usually make a sandwich or a bowl of rice with chicken and a fresh vegetable salad. "
            "Cucumber, tomato, carrot, onion, and a bit of pepper make it taste better. "
            "I don’t add too much salt or sugar — I want the meal to feel light.",
            "Với lunch tôi thường làm sandwich hoặc một tô rice với chicken và salad vegetable tươi. "
            "Cucumber, tomato, carrot, onion, và một chút pepper làm món ngon hơn. "
            "Tôi không cho quá nhiều salt hay sugar — tôi muốn meal nhẹ nhàng.",
        ),
        (
            "In the evening, dinner is my favourite meal of the day. "
            "Sometimes we share pizza, sometimes we cook soup with potato and meat, "
            "or fish when we want something lighter. "
            "A glass of water or fresh juice is enough for me with dinner.",
            "Buổi tối, dinner là meal yêu thích trong ngày. "
            "Đôi khi chúng tôi chia pizza, đôi khi nấu soup với potato và meat, "
            "hoặc fish khi muốn món nhẹ hơn. "
            "Một ly water hoặc juice tươi là đủ với dinner.",
        ),
        (
            "After meals I love fruit — an apple, an orange, a banana, a peach, a grape, or a slice of lemon in my drink. "
            "On weekends there is cake or a cookie, and ice cream with cream if friends come over. "
            "Honestly, honey on warm bread is still my favourite small treat.",
            "Sau các bữa ăn tôi thích fruit — apple, orange, banana, peach, grape, hoặc lát lemon trong đồ uống. "
            "Cuối tuần có cake hoặc cookie, và ice cream với cream nếu bạn bè tới chơi. "
            "Thành thật mà nói, honey trên bread nóng vẫn là món nhỏ yêu thích của tôi.",
        ),
    ],
    "A2": [
        (
            "I’d like to talk about a weekend on my uncle’s farm. "
            "Farming there is slow and peaceful — we plant seeds, water the soil, pick ripe fruit, "
            "and grow vegetables that we can produce and feed the family with all summer.",
            "Tôi muốn nói về một cuối tuần ở farm của chú. "
            "Farming ở đó chậm rãi và yên — chúng tôi plant hạt, water đất, pick trái chín, "
            "và grow rau để produce và feed cả nhà suốt mùa hè.",
        ),
        (
            "In the garden I picked strawberry, blueberry, watermelon, pear, pineapple, mango, kiwi, avocado, and grapefruit. "
            "Between the fruit trees there were flowers too — a rose, a lily, an orchid, a sunflower, and even a small cactus. "
            "I love how soft fruit smells sweet, while a hard nut needs more work before you can taste it.",
            "Trong vườn tôi hái strawberry, blueberry, watermelon, pear, pineapple, mango, kiwi, avocado, và grapefruit. "
            "Giữa các cây còn có hoa — rose, lily, orchid, sunflower, và cả cactus nhỏ. "
            "Tôi thích fruit mềm smell ngọt, còn nut hard thì cần thêm công trước khi taste.",
        ),
        (
            "For snacks we cracked peanut, walnut, hazelnut, almond, and pecan. "
            "Later my aunt opened a cookbook and made an omelet with pork, a little beef, lamb on the side, and tuna for my cousin. "
            "We kept the leftovers in the fridge for the rest of the week after a quick grocery run for sauce and pasta.",
            "Làm snack chúng tôi tách peanut, walnut, hazelnut, almond, và pecan. "
            "Sau đó dì mở cookbook và làm omelet với pork, chút beef, lamb bên cạnh, và tuna cho anh họ. "
            "Chúng tôi giữ leftovers trong tủ cho rest của tuần sau khi đi grocery nhanh lấy sauce và pasta.",
        ),
        (
            "On Sunday we went out. At the coffee shop I ordered hot chocolate, then we looked at the menu. "
            "My friend is vegetarian, and her sister is vegan, so they chose broccoli, celery, eggplant, cabbage, spinach, pea, bean, and mushroom. "
            "I ordered a steak — medium, not rare and not well-done — because watery meat has a bad taste to me.",
            "Chủ nhật chúng tôi đi chơi. Ở coffee shop tôi order hot chocolate, rồi xem menu. "
            "Bạn tôi là vegetarian, còn chị ấy vegan, nên họ chọn broccoli, celery, eggplant, cabbage, spinach, pea, bean, và mushroom. "
            "Tôi order steak — medium, không rare cũng không well-done — vì meat watery có taste tệ với tôi.",
        ),
        (
            "Someone asked for a spicy noodle bowl; someone else wanted salty French fries and a potato chip snack. "
            "I prefer fresh flavor to bitter junk food, though a sweet dessert like pie or dark chocolate is fine after dinner. "
            "They also serve hamburger, hot dog, sausage, toast, and delicious pasta with a tip jar by the door — yes, we did tip. "
            "Before I order, I always taste a sample to check the taste if the shop offers one.",
            "Ai đó gọi một tô noodle spicy; người khác muốn French fries salty và snack potato chip. "
            "Tôi thích flavor fresh hơn junk food bitter, dù dessert sweet như pie hoặc dark chocolate thì ổn sau dinner. "
            "Họ cũng serve hamburger, hot dog, sausage, toast, và pasta delicious với lọ tip gần cửa — đúng, chúng tôi có tip. "
            "Trước khi order, tôi luôn taste mẫu để kiểm tra taste nếu quán cho thử.",
        ),
        (
            "Honestly, fast food is easy, but farm fruit still wins. "
            "If a dish tastes sour or too spicy, I just ask them to fry something milder next time. "
            "That weekend felt complete — from planting on the farm to one last order at the coffee shop.",
            "Thành thật, fast food thì tiện, nhưng fruit từ farm vẫn thắng. "
            "Nếu món taste sour hoặc quá spicy, tôi chỉ nhờ họ fry món nhẹ hơn lần sau. "
            "Cuối tuần đó trọn vẹn — từ planting trên farm đến order cuối ở coffee shop.",
        ),
    ],
    "B1": [
        (
            "Yes, definitely. I’m a big fan of nonalcoholic beverages, especially in the morning. "
            "My favourite drink is a latte made with a shot of espresso. "
            "This is because it gives me the chance to wake up slowly without feeling jittery. "
            "Honestly, a strong black espresso alone is a bit too intense for me.",
            "Chắc chắn rồi. Tôi rất thích beverage nonalcoholic, đặc biệt buổi sáng. "
            "Đồ uống yêu thích của tôi là latte với một shot espresso. "
            "Vì vậy tôi tỉnh dậy từ từ mà không bị kích thích quá. "
            "Thành thật, chỉ espresso đen đặc thôi thì hơi mạnh với tôi.",
        ),
        (
            "I prefer drinking mineral water or homemade lemonade to soft drinks like soda or Coca-Cola, "
            "while those fizzy drinks can feel fun for a moment, they are packed with sugar. "
            "I hardly ever buy an energy drink — to be honest, I find the taste artificial. "
            "How often? I usually drink a smoothie two or three times a week, and sometimes treat myself to a milkshake when I’m out with friends. "
            "On cold evenings I go for cocoa instead of coffee.",
            "Tôi thích mineral water hoặc lemonade nhà làm hơn soft drink như soda hay Coca-Cola, "
            "dù đồ có gas vui một lúc nhưng nhiều đường. "
            "Tôi hầu như không mua energy drink — nói thiệt, vị nó giả tạo. "
            "Thường xuyên thế nào? Tôi uống smoothie khoảng hai ba lần một tuần, và thỉnh thoảng milkshake khi đi với bạn. "
            "Tối lạnh tôi chọn cocoa thay vì cà phê.",
        ),
        (
            "As for alcoholic drinks, I rarely drink alcohol — maybe a glass of wine or Champagne when we celebrate, "
            "but beer, whiskey, vodka, tequila, or brandy almost never. "
            "If I want bubbles, I choose sparkling water rather than still, and I skip complicated cocktails with Tonic. "
            "Keeping things simple is a piece of cake for me.",
            "Còn alcoholic drink thì tôi hiếm khi drink alcohol — có lẽ một ly wine hoặc Champagne khi ăn mừng, "
            "nhưng beer, whiskey, vodka, tequila hay brandy thì gần như không. "
            "Nếu muốn có gas, tôi chọn nước sparkling thay vì still, và bỏ cocktail phức tạp với Tonic. "
            "Giữ mọi thứ đơn giản với tôi là chuyện dễ như ăn bánh.",
        ),
        (
            "I’d like to talk about a weekend brunch near my house. "
            "First, I ordered crispy bacon and a soft-boiled egg so I could dip toast into the yolk while the white was just set. "
            "My friend preferred white meat, so she chose a grilled chicken breast and a wing. "
            "I usually avoid too much red meat, but that day I shared ribs and a small hamburger made from juicy flesh — "
            "plus turkey, ham, a meatball, and even duck for the adventurous ones. "
            "I’m still not into rabbit, veal, or goose, and a huge joint of meat feels too heavy for brunch.",
            "Tôi muốn kể về brunch cuối tuần gần nhà. "
            "Đầu tiên tôi gọi bacon giòn và trứng luộc để chấm yolk khi white vừa đông. "
            "Bạn tôi thích white meat nên chọn breast gà nướng và vài wing. "
            "Tôi thường tránh red meat nhiều, nhưng hôm đó chia rib và hamburger nhỏ từ flesh mọng — "
            "cộng turkey, ham, meatball, và cả duck cho người thích thử. "
            "Tôi vẫn chưa mê rabbit, veal hay goose, và một joint thịt lớn thì quá nặng cho brunch.",
        ),
        (
            "For seafood lovers there was shellfish — oyster, crab, even lobster. "
            "The cheese board had Gouda, Cheddar, Swiss cheese, cream cheese on crackers, and a little blue cheese that was strong for me. "
            "Someone ordered a cut of steak beside mashed potato, green bean, and lettuce with garlic and mint. "
            "I added black pepper, a pickle, and peanut butter on a warm bread roll from a fresh loaf.",
            "Người mê seafood có shellfish — oyster, crab, thậm chí lobster. "
            "Khay phô mai có Gouda, Cheddar, Swiss cheese, cream cheese trên bánh cracker, và chút blue cheese hơi mạnh với tôi. "
            "Ai đó gọi một cut steak cạnh mashed potato, green bean, và lettuce với garlic cùng mint. "
            "Tôi thêm black pepper, pickle, và peanut butter trên bread roll nóng từ loaf mới.",
        ),
        (
            "On another day I tried a plant-based wrap with raw cucumber vibes — actually ripe fruit salad with berry, cherry, blackberry, cranberry, and citrus. "
            "I packed tangerine, mandarin, tangelo, lime, nectarine, plum, apricot, fig, date, olive, pumpkin, coconut, and papaya. "
            "There was also melon and cantaloupe, plus pomegranate seeds, chestnut, macadamia nut, pistachio, and cashew for crunch.",
            "Ngày khác tôi thử wrap plant-based kiểu raw — thực ra là fruit salad chín với berry, cherry, blackberry, cranberry, và citrus. "
            "Tôi mang theo tangerine, mandarin, tangelo, lime, nectarine, plum, apricot, fig, date, olive, pumpkin, coconut, và papaya. "
            "Còn melon với cantaloupe, hạt pomegranate, chestnut, macadamia nut, pistachio, và cashew cho độ giòn.",
        ),
        (
            "About diet: I’ve tested a low-fat diet, a low-carb diet, and even a gluten-free diet when friends asked. "
            "I still watch every calorie and care about nutrition, but I don’t panic over chocolate, a cupcake, a donut, cheesecake, Jell-O, or popcorn at the cinema. "
            "Sugar-free lemonade and a croissant with curry leftover from take-away can share the same week — balance matters more than perfection.",
            "Về diet: tôi đã thử low-fat diet, low-carb diet, và cả gluten-free diet khi bạn nhờ. "
            "Tôi vẫn để ý calorie và nutrition, nhưng không hoảng vì chocolate, cupcake, donut, cheesecake, Jell-O, hay popcorn lúc xem phim. "
            "Lemonade sugar-free và croissant với curry leftover từ take-away có thể chung một tuần — cân bằng quan trọng hơn hoàn hảo.",
        ),
        (
            "Last week I also made pancake with pepper from the fridge, a cheeseburger for my brother, and a simple curry with green bean. "
            "If the fruit isn’t ripe, I wait; if I want something quick, take-away is fine. "
            "That’s how I talk about food now — like a short blog entry I’d actually say out loud in the speaking room.",
            "Tuần trước tôi cũng làm pancake với pepper trong tủ, cheeseburger cho em, và curry đơn giản với green bean. "
            "Nếu fruit chưa ripe tôi đợi; nếu muốn nhanh thì take-away cũng được. "
            "Đó là cách tôi nói về đồ ăn bây giờ — như một blog ngắn tôi thật sự nói ra trong phòng speaking.",
        ),
    ],
    "B2": [
        (
            "Yes, definitely. I’m a big fan of exploring different kinds of cuisine. "
            "My favourite weekend habit is to sip a cappuccino made with skim milk and then grab a bagel with goat cheese. "
            "This is because it feels light but still satisfying — not a heavy portion like a full beefsteak. "
            "I prefer herbal tea or ice tea with a straw and an ice cube or two to sugary drinks, "
            "while my friends often order a mojito, margarita, martini, or even a Bloody Mary.",
            "Chắc chắn rồi. Tôi thích khám phá nhiều loại cuisine. "
            "Thói quen cuối tuần yêu thích là sip cappuccino với skim milk rồi lấy bagel với goat cheese. "
            "Vì nó nhẹ mà vẫn đủ no — không phải portion nặng như beefsteak nguyên miếng. "
            "Tôi thích herbal tea hoặc ice tea với straw và vài ice cube hơn đồ ngọt, "
            "còn bạn bè thường gọi mojito, margarita, martini, hoặc cả Bloody Mary.",
        ),
        (
            "I hardly ever buy booze from a liquor store; if I drink liquor at all, it’s maybe cider, a splash of gin, Bourbon, or ginger ale as a mixer. "
            "After a late party I need time to sober up, so I ask for a refill of water when thirst hits, and I skip punch if it tastes too strong. "
            "Chewing gum, a hard candy, or a lollipop helps after coffee — silly, but it works.",
            "Tôi hầu như không mua booze ở liquor store; nếu có uống liquor thì có lẽ cider, chút gin, Bourbon, hoặc ginger ale để pha. "
            "Sau tiệc muộn tôi cần thời gian sober up, nên xin refill nước khi thirst tới, và bỏ punch nếu quá mạnh. "
            "Chewing gum, hard candy, hoặc lollipop giúp sau cà phê — hơi buồn cười nhưng hiệu quả.",
        ),
        (
            "I’d like to talk about a family supper we cooked last month. "
            "First, I heat the stove and open a recipe with every ingredient on the counter: "
            "herb, spice, beet, green pepper, red pepper, zucchini, sweet potato, raspberry, and wheat flour for a baguette and soft roll. "
            "I used a scale for a cupful of flour, a pinch of salt, and a spoonful of tomato paste.",
            "Tôi muốn kể về supper gia đình tháng trước. "
            "Đầu tiên tôi heat bếp và mở recipe với mọi ingredient trên counter: "
            "herb, spice, beet, green pepper, red pepper, zucchini, sweet potato, raspberry, và bột wheat cho baguette cùng roll mềm. "
            "Tôi dùng scale cho cupful bột, pinch muối, và spoonful tomato paste.",
        ),
        (
            "With a wooden spoon in a mixing bowl, I beat eggs, then chop vegetables finely and marinate the meat. "
            "I peel vegetables, slice them thin, stir a white sauce, and roast sweet potato while I grill kebab outside on the barbecue. "
            "Sometimes I poach an egg, toast cereal crumbs on pastry, or fry in a frying pan and a wok with the lid half closed.",
            "Với wooden spoon trong mixing bowl, tôi beat trứng, rồi chop rau, và marinate thịt. "
            "Tôi peel rau, slice mỏng, stir white sauce, và roast sweet potato trong lúc grill kebab ngoài barbecue. "
            "Đôi khi tôi poach trứng, toast vụn cereal trên pastry, hoặc chiên bằng frying pan và wok với lid hé.",
        ),
        (
            "Every utensil mattered — blender, mixer, even the old scale. "
            "Mom made meatloaf with mayonnaise, mustard, soy sauce, ketchup, and a splash of vinegar; "
            "I added margarine or sour cream on the side, never too much carbohydrate in one plate. "
            "We finished with pudding, a popsicle for the kids, and one more garnish of raspberry on top.",
            "Mọi utensil đều quan trọng — blender, mixer, cả scale cũ. "
            "Mẹ làm meatloaf với mayonnaise, mustard, soy sauce, ketchup, và chút vinegar; "
            "tôi thêm margarine hoặc sour cream bên cạnh, không để quá nhiều carbohydrate trên một đĩa. "
            "Chúng tôi kết thúc bằng pudding, popsicle cho trẻ, và thêm garnish raspberry lên trên.",
        ),
        (
            "If nobody wants to cook, takeout is fine — a portion of kebab or leftover roll with tomato paste warmed up. "
            "That’s my food blog voice now: real kitchen verbs, real drinks, and vocabulary I’d reuse in IELTS speaking without sounding like a word list.",
            "Nếu không ai muốn nấu, takeout cũng được — một portion kebab hoặc roll leftover với tomato paste hâm nóng. "
            "Đó là giọng blog đồ ăn của tôi giờ: động từ bếp thật, đồ uống thật, và từ vựng tôi tái sử dụng trong IELTS speaking mà không giống danh sách từ.",
        ),
    ],
}


def build_from_passages(level: str, words: list[dict]) -> list[dict]:
    paras = PASSAGES[level]
    sentences = []
    for en, vi in paras:
        sentences.append(
            {
                "en_html": mark_sentence(en, words),
                "vi": vi,
                "words": [],
            }
        )
    missing = verify_coverage(words, sentences)
    if missing:
        # Append a natural closing line that forces remaining forms in
        miss_items = [w for w in words if w["word"] in missing]
        # chunk into readable spoken lines
        for i in range(0, len(miss_items), 6):
            chunk = miss_items[i : i + 6]
            forms = [w["form"] for w in chunk]
            if len(forms) == 1:
                en = f"And one more word I keep using when I talk about food is {forms[0]}."
                vi = f"Và thêm một từ tôi hay dùng khi nói về đồ ăn là {forms[0]}."
            elif len(forms) == 2:
                en = f"When I wrap up this topic, I also mention {forms[0]} and {forms[1]}."
                vi = f"Khi kết thúc chủ đề này, tôi cũng nhắc {forms[0]} và {forms[1]}."
            else:
                mid = ", ".join(forms[:-1])
                en = (
                    f"To finish this food blog entry the way I’d speak in an exam, "
                    f"I also bring in {mid}, and finally {forms[-1]}."
                )
                vi = (
                    f"Để kết thúc blog đồ ăn theo cách tôi nói trong phòng thi, "
                    f"tôi cũng nhắc {mid}, và cuối cùng {forms[-1]}."
                )
            # ensure every form is literally present
            for w in chunk:
                if not re.search(rf"(?i)(?<![A-Za-z]){re.escape(w['form'])}(?![A-Za-z])", en):
                    en += f" ({w['form']})"
            sentences.append(
                {
                    "en_html": mark_sentence(en, chunk),
                    "vi": vi,
                    "words": [w["word"] for w in chunk],
                }
            )
    return sentences


def main() -> None:
    topic = next(t for t in TOPICS["topics"] if t["slug"] == "food-drink")
    for level in ["A1", "A2", "B1", "B2"]:
        lessons = [l for l in topic["lessons"] if l["level"] == level]
        words = collect_words([l["id"] for l in lessons])
        sentences = build_from_passages(level, words)
        missing = verify_coverage(words, sentences)
        page = wrap_exercise(
            topic,
            level,
            words,
            sentences,
            [l["title"] for l in lessons],
        )
        # Slightly richer lede for speaking focus
        page = page.replace(
            "Reading passage with every new word from this level’s LanGeek lessons — IPA, highlights, sentence translation, and free TTS.",
            "Daily food blog / speaking-style passage — every new word from this level’s LanGeek lessons, with IPA, highlights, VI toggle, and TTS (IPA is display-only).",
        )
        out_dir = OUT / f"{level.lower()}-exercise"
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "index.html").write_text(page, encoding="utf-8")
        print(f"{level}: {len(words)} words, {len(sentences)} paras, missing={len(missing)}")
        if missing:
            print("  still missing:", missing)


if __name__ == "__main__":
    main()
