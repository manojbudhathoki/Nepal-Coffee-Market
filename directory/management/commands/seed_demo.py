from django.core.management.base import BaseCommand
from django.utils.text import slugify
from directory.models import Producer, CoffeeProduct, Recipe
class Command(BaseCommand):
    help = 'Create clearly labelled fictional demo data for local development.'
    def handle(self, *args, **kwargs):
        demo = [
          {'name':'Demo Hillside Coffee Cooperative','slug':'demo-hillside-coffee','province':'Bagmati Province','district':'Kavrepalanchok','municipality':'Panauti','rating':'4.7','featured':True,'verified':False,'tagline':'A sample listing — replace with a real producer','description':'Fictional development content only. Replace this profile with confirmed information from a real Nepali coffee producer.'},
          {'name':'Demo Green Valley Roastery','slug':'demo-green-valley-roastery','province':'Gandaki Province','district':'Kaski','municipality':'Pokhara','rating':'4.5','featured':True,'verified':False,'tagline':'A sample roastery listing','description':'Fictional development content only. Replace this profile with confirmed information from a real Nepali coffee producer.'},
          {'name':'Demo Eastern Mountain Coffee','slug':'demo-eastern-mountain-coffee','province':'Koshi Province','district':'Ilam','municipality':'Suryodaya','rating':'4.3','featured':False,'verified':False,'tagline':'A sample origin listing','description':'Fictional development content only. Replace this profile with confirmed information from a real Nepali coffee producer.'},
        ]
        for data in demo:
            p, _ = Producer.objects.update_or_create(slug=data['slug'], defaults=data)
            CoffeeProduct.objects.get_or_create(producer=p, slug='house-arabica', defaults={'name':'House Arabica (Demo)','description':'Sample product; price is illustrative and not an offer.','coffee_type':'arabica','process':'washed','roast_level':'Medium','price_npr':650,'unit_label':'250 g','available_for_export':False,'in_stock':True})
        recipes = [
          ('Nepali-style Milk Coffee','nepali-style-milk-coffee','Comforting stovetop coffee with milk and a little sweetness.','Ground coffee,Milk,Water,Sugar (optional)','Heat water and milk gently in a pan. Add coffee and simmer briefly. Strain into a cup. Sweeten to taste.'),
          ('Pour-over Coffee','pour-over-coffee','A clean cup that highlights the character of the beans.','15 g medium-ground coffee,250 ml hot water,Filter paper','Rinse the filter with hot water. Add coffee grounds. Pour a little water to bloom for 30 seconds. Slowly pour the remaining water in circles. Serve fresh.'),
          ('Iced Coffee','iced-coffee','A refreshing cold coffee for warm afternoons.','60 ml strong brewed coffee,120 ml milk,Ice,Syrup (optional)','Brew coffee and let it cool. Fill a glass with ice. Add coffee and milk. Stir and sweeten if desired.'),
          ('French Press','french-press','A full-bodied brewing method with very little equipment.','30 g coarsely ground coffee,500 ml hot water','Add coffee to a clean French press. Pour hot water and stir gently. Steep for 4 minutes. Press slowly and serve immediately.'),
        ]
        for title, slug, intro, ingredients, instructions in recipes:
            Recipe.objects.get_or_create(slug=slug, defaults={'title':title,'intro':intro,'ingredients':ingredients.replace(',', '\n'),'instructions':instructions.replace('. ', '.\n')})
        self.stdout.write(self.style.SUCCESS('Demo content created. All demo producers/products are fictional; replace before launch.'))
