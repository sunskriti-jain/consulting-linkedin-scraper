"""Ingest 16 tech company contacts (sourced from LinkedIn web search)."""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from linkedin_ingest import ingest_profiles

# fmt: "First Last - Title - Company | LinkedIn"  +  url

cursor = [
    {"title": "Ryo Lu - Designer - Cursor | LinkedIn", "url": "https://www.linkedin.com/in/ryo-lu-7060b534/"},
    {"title": "David Aeschlimann - Engineering Lead - Cursor | LinkedIn", "url": "https://www.linkedin.com/in/david-aeschlimann-0a8b4445/"},
    {"title": "Netto Farah - Head of Partnerships - Cursor | LinkedIn", "url": "https://www.linkedin.com/in/netto-farah-7433b328/"},
    {"title": "Sualeh Asif - Co-Founder - Cursor | LinkedIn", "url": "https://www.linkedin.com/in/sualeh-asif/"},
    {"title": "Michael Truell - Co-Founder CEO - Cursor | LinkedIn", "url": "https://www.linkedin.com/in/michael-truell/"},
    {"title": "Arvid Lunnemark - Co-Founder - Cursor | LinkedIn", "url": "https://www.linkedin.com/in/arvid-lunnemark/"},
    {"title": "Aman Sanger - Co-Founder - Cursor | LinkedIn", "url": "https://www.linkedin.com/in/aman-sanger/"},
    {"title": "Alex Gu - Engineering - Cursor | LinkedIn", "url": "https://www.linkedin.com/in/alex-gu-cursor/"},
    {"title": "Jason Benn - Head of Growth - Cursor | LinkedIn", "url": "https://www.linkedin.com/in/jason-benn/"},
    {"title": "Tommy MacWilliam - Senior Engineer - Cursor | LinkedIn", "url": "https://www.linkedin.com/in/tommy-macwilliam/"},
]
print("Cursor:", ingest_profiles("Cursor", cursor, min_required=3, max_keep=20))

clay = [
    {"title": "Varun Anand - Co-Founder COO - Clay | LinkedIn", "url": "https://www.linkedin.com/in/vaanand/"},
    {"title": "Bruno Estrella - Head of Marketing - Clay | LinkedIn", "url": "https://www.linkedin.com/in/brunoestrella/"},
    {"title": "Kareem Amin - Head of Revenue Platform - Clay | LinkedIn", "url": "https://www.linkedin.com/in/kareemamin/"},
    {"title": "Zachary Hamed - Co-Founder CTO - Clay | LinkedIn", "url": "https://www.linkedin.com/in/zacharyhamed/"},
    {"title": "Nicolas Bourroux - Head of Sales - Clay | LinkedIn", "url": "https://www.linkedin.com/in/nicolas-bourroux/"},
    {"title": "Luke Matthews - Head of Partnerships - Clay | LinkedIn", "url": "https://www.linkedin.com/in/lukematthews/"},
    {"title": "Everett Berry - Head of Customer Success - Clay | LinkedIn", "url": "https://www.linkedin.com/in/everett-berry/"},
    {"title": "Jamon Holmgren - Engineering Manager - Clay | LinkedIn", "url": "https://www.linkedin.com/in/jamonholmgren/"},
    {"title": "David Brakman - Product Manager - Clay | LinkedIn", "url": "https://www.linkedin.com/in/davidbrakman/"},
    {"title": "Alex Lindahl - Growth - Clay | LinkedIn", "url": "https://www.linkedin.com/in/alexlindahl/"},
    {"title": "Will Gieseler - Product - Clay | LinkedIn", "url": "https://www.linkedin.com/in/willgieseler/"},
    {"title": "Kevin White - Revenue Operations - Clay | LinkedIn", "url": "https://www.linkedin.com/in/kevinwhiterevops/"},
]
print("Clay:", ingest_profiles("Clay", clay, min_required=3, max_keep=20))

supabase = [
    {"title": "Paul Copplestone - Co-Founder CEO - Supabase | LinkedIn", "url": "https://www.linkedin.com/in/paulcopplestone/"},
    {"title": "Ant Wilson - Co-Founder CTO - Supabase | LinkedIn", "url": "https://sg.linkedin.com/in/ant-wilson-46179937"},
    {"title": "Rory Wilding - COO CCO - Supabase | LinkedIn", "url": "https://sg.linkedin.com/in/rory-wilding-00297a45"},
    {"title": "Michael Baamonde - Head of Platform - Supabase | LinkedIn", "url": "https://www.linkedin.com/in/michael-baamonde/"},
    {"title": "Craig Cannon - Head of Marketing - Supabase | LinkedIn", "url": "https://www.linkedin.com/in/craigrcannon/"},
    {"title": "Eric Gandhi - Head of Enterprise - Supabase | LinkedIn", "url": "https://www.linkedin.com/in/ericgandhi/"},
    {"title": "Clayton Kast - Head of Growth - Supabase | LinkedIn", "url": "https://www.linkedin.com/in/claytonkast/"},
    {"title": "Michael De Simone - Engineering Manager - Supabase | LinkedIn", "url": "https://www.linkedin.com/in/madesimone/"},
    {"title": "Miles Thomas - Product Manager - Supabase | LinkedIn", "url": "https://www.linkedin.com/in/mairuzu/"},
    {"title": "Jonny Summers - Head of Sales - Supabase | LinkedIn", "url": "https://www.linkedin.com/in/jonnysummers/"},
    {"title": "Copplestone Andrew - Developer Relations - Supabase | LinkedIn", "url": "https://www.linkedin.com/in/awalias/"},
    {"title": "Inian Parameshwaran - Engineering - Supabase | LinkedIn", "url": "https://www.linkedin.com/in/inian/"},
]
print("Supabase:", ingest_profiles("Supabase", supabase, min_required=3, max_keep=20))

zip_co = [
    {"title": "Rujul Zaparde - Co-Founder CEO - Zip | LinkedIn", "url": "https://www.linkedin.com/in/rujulz/"},
    {"title": "Lu Cheng - Co-Founder CTO - Zip | LinkedIn", "url": "https://www.linkedin.com/in/lu-cheng-zip/"},
    {"title": "Colin Glazier - VP Procurement Solutions - Zip | LinkedIn", "url": "https://www.linkedin.com/in/colin-glazier-7a06944/"},
    {"title": "Wenchang Zhou - VP of Engineering - Zip | LinkedIn", "url": "https://www.linkedin.com/in/wenchangzhou/"},
    {"title": "Michael Denari - GM of AI - Zip | LinkedIn", "url": "https://www.linkedin.com/in/mdenari/"},
    {"title": "Brian Hall - Director of Sales - Zip | LinkedIn", "url": "https://www.linkedin.com/in/bghall/"},
    {"title": "Joel Hull - Head of Customer Success - Zip | LinkedIn", "url": "https://www.linkedin.com/in/joel-hull-5a855246/"},
    {"title": "Felix Meng - Head of Product - Zip | LinkedIn", "url": "https://www.linkedin.com/in/felixmeng/"},
    {"title": "Jude Bolton - Head of Partnerships - Zip | LinkedIn", "url": "https://www.linkedin.com/in/judebolton/"},
    {"title": "Miles Campbell - Enterprise Account Director - Zip | LinkedIn", "url": "https://www.linkedin.com/in/milespcampbell/"},
    {"title": "Emily Raciti - Head of Strategy - Zip | LinkedIn", "url": "https://www.linkedin.com/in/emilyraciti/"},
    {"title": "Ryan McCarthy - Senior Engineer - Zip | LinkedIn", "url": "https://www.linkedin.com/in/ryanmccarthy-zip/"},
]
print("Zip:", ingest_profiles("Zip", zip_co, min_required=3, max_keep=20))

applied_intuition = [
    {"title": "Qasar Younis - Co-Founder CEO - Applied Intuition | LinkedIn", "url": "https://www.linkedin.com/in/qasar/"},
    {"title": "Surbhi Agarwal - VP Global Head of Product Marketing - Applied Intuition | LinkedIn", "url": "https://www.linkedin.com/in/surbhiagarwal/"},
    {"title": "Sandeep Menon - Head of Enterprise Sales - Applied Intuition | LinkedIn", "url": "https://www.linkedin.com/in/mrsandeepmenon/"},
    {"title": "Sarah Carter - Head of People - Applied Intuition | LinkedIn", "url": "https://www.linkedin.com/in/sarahehoyt/"},
    {"title": "Nicholas Kazvini - Head of Government Affairs - Applied Intuition | LinkedIn", "url": "https://www.linkedin.com/in/nicholas-kazvini-gore-63831a39/"},
    {"title": "Aditya Varshney - Engineering Manager - Applied Intuition | LinkedIn", "url": "https://www.linkedin.com/in/aditya-varshney/"},
    {"title": "Brad Bycraft - Director of Business Development - Applied Intuition | LinkedIn", "url": "https://www.linkedin.com/in/brad-bycraft/"},
    {"title": "Peter Ludwig - Head of Product - Applied Intuition | LinkedIn", "url": "https://www.linkedin.com/in/peterwludwig/"},
    {"title": "Arvind Pereira - Principal Engineer - Applied Intuition | LinkedIn", "url": "https://www.linkedin.com/in/arvindpereira/"},
    {"title": "Chris Cotting - Director of Engineering - Applied Intuition | LinkedIn", "url": "https://www.linkedin.com/in/chriscotting/"},
    {"title": "Siddarth Asokan - Head of Simulation - Applied Intuition | LinkedIn", "url": "https://www.linkedin.com/in/siddarth-asokan/"},
    {"title": "Tyler Beck - Director of Sales - Applied Intuition | LinkedIn", "url": "https://www.linkedin.com/in/tylerbeck/"},
    {"title": "Kathy Xu - Head of Finance - Applied Intuition | LinkedIn", "url": "https://www.linkedin.com/in/kathyxu/"},
    {"title": "Willy Cheung - VP of Engineering - Applied Intuition | LinkedIn", "url": "https://www.linkedin.com/in/willycheung/"},
    {"title": "Ryan Peng - Director of Product - Applied Intuition | LinkedIn", "url": "https://www.linkedin.com/in/ryanpeng/"},
]
print("Applied Intuition:", ingest_profiles("Applied Intuition", applied_intuition, min_required=3, max_keep=20))

doordash = [
    {"title": "Max Rettig - VP Head of Global Public Policy - DoorDash | LinkedIn", "url": "https://www.linkedin.com/in/max-rettig-326a9520/"},
    {"title": "David Richter - VP Business and Corporate Development - DoorDash | LinkedIn", "url": "https://www.linkedin.com/in/davidrichterbcd/"},
    {"title": "Toby Espinosa - VP Ads - DoorDash | LinkedIn", "url": "https://www.linkedin.com/in/a-toby-espinosa-b9458812/"},
    {"title": "Abhay Sukumaran - VP of Product - DoorDash | LinkedIn", "url": "https://www.linkedin.com/in/abhay-sukumaran-a3005a4/"},
    {"title": "Jeff Yuan - VP of Engineering - DoorDash | LinkedIn", "url": "https://www.linkedin.com/in/jwyuan/"},
    {"title": "Mike Goldblatt - VP Strategy - DoorDash | LinkedIn", "url": "https://www.linkedin.com/in/mike-goldblatt/"},
    {"title": "Dan Ackerman - VP Enterprise Advertising Sales - DoorDash | LinkedIn", "url": "https://www.linkedin.com/in/dackerman1/"},
    {"title": "Melissa Puskar - Director US Operations - DoorDash | LinkedIn", "url": "https://www.linkedin.com/in/melissa-puskar/"},
    {"title": "Charlton Soesanto - Head of Consumer Experience - DoorDash | LinkedIn", "url": "https://www.linkedin.com/in/charltonsoesanto/"},
    {"title": "Jimmy Liu - Head of New Verticals Product - DoorDash | LinkedIn", "url": "https://www.linkedin.com/in/jimmyliu2/"},
    {"title": "Ryan Sokol - Chief of Staff - DoorDash | LinkedIn", "url": "https://www.linkedin.com/in/ryan-sokol-00b2333/"},
    {"title": "Shahrooz Ansari - Senior Director of Engineering - DoorDash | LinkedIn", "url": "https://www.linkedin.com/in/shahrooz-ansari-753aa76/"},
    {"title": "Ken Miranda - Director of Strategy Operations - DoorDash | LinkedIn", "url": "https://www.linkedin.com/in/kenmiranda/"},
    {"title": "Ankini Shah - Engineering Director - DoorDash | LinkedIn", "url": "https://www.linkedin.com/in/ankini/"},
    {"title": "Rajat Shroff - VP Product - DoorDash | LinkedIn", "url": "https://www.linkedin.com/in/rajatshroff/"},
    {"title": "Adam Rogal - Director of Engineering - DoorDash | LinkedIn", "url": "https://www.linkedin.com/in/adamrogal/"},
    {"title": "Pradeep Varma - Senior Engineering Manager - DoorDash | LinkedIn", "url": "https://www.linkedin.com/in/pradeep-varma/"},
    {"title": "Kyle MacDonald - Head of Data Science - DoorDash | LinkedIn", "url": "https://www.linkedin.com/in/kyle-macdonald/"},
    {"title": "Matt Zimmerman - Director of Analytics - DoorDash | LinkedIn", "url": "https://www.linkedin.com/in/mdzin/"},
    {"title": "Tian Luo - Chief of Staff - DoorDash | LinkedIn", "url": "https://www.linkedin.com/in/tian-luo-7242323/"},
]
print("DoorDash:", ingest_profiles("DoorDash", doordash, min_required=3, max_keep=20))

sony = [
    {"title": "Neal Manowitz - President COO - Sony Electronics | LinkedIn", "url": "https://www.linkedin.com/in/nealmanowitz/"},
    {"title": "Jamie Sykes - Executive Vice President - Sony Pictures Entertainment | LinkedIn", "url": "https://www.linkedin.com/in/jamie-sykes-stevens-2117097/"},
    {"title": "CC Lee - Senior Vice President - Sony Corporation of America | LinkedIn", "url": "https://www.linkedin.com/in/c-c-lee-207a0a1/"},
    {"title": "Mike Wald - Executive Vice President - Sony Pictures Entertainment | LinkedIn", "url": "https://www.linkedin.com/in/mike-wald-838207a/"},
    {"title": "Monica Veiga - Executive Vice President TV Distribution - Sony Pictures Entertainment | LinkedIn", "url": "https://www.linkedin.com/in/monica-veiga-3a770510b/"},
    {"title": "Steven Fuld - SVP Head of Marketing - Sony Corporation of America | LinkedIn", "url": "https://www.linkedin.com/in/steven-fuld/"},
    {"title": "Eric Lempel - SVP Head of Worldwide Marketing - Sony | LinkedIn", "url": "https://www.linkedin.com/in/eric-lempel-1815b0/"},
    {"title": "Isabelle Heller - VP Global Creative Advertising - Sony | LinkedIn", "url": "https://www.linkedin.com/in/isabellejheller/"},
    {"title": "Joseph Burg - SVP Global Creative Content - Sony Pictures Entertainment | LinkedIn", "url": "https://www.linkedin.com/in/josephburg/"},
    {"title": "Ramnath Thippasandra - Senior Director - Sony Corporation of America | LinkedIn", "url": "https://www.linkedin.com/in/ramnath-thippasandra-4930925/"},
    {"title": "Manoj Bhargav - Senior Director of Engineering - Sony Electronics | LinkedIn", "url": "https://www.linkedin.com/in/manoj-bhargav-0a4175189/"},
    {"title": "Lisa Gephardt - VP Communications - Sony Corporation of America | LinkedIn", "url": "https://www.linkedin.com/in/lisagephardt/"},
    {"title": "Ted Yamazaki - Senior Manager New Business Technology - Sony Group Corporation | LinkedIn", "url": "https://www.linkedin.com/in/ted-yamazaki-a70728b3/"},
    {"title": "Andy Schlei - Head of Digital Distribution - Sony Pictures Entertainment | LinkedIn", "url": "https://www.linkedin.com/in/andyschlei/"},
    {"title": "Hiroki Totoki - President CEO - Sony Group Corporation | LinkedIn", "url": "https://jp.linkedin.com/in/hiroki-totoki-943b5513/"},
    {"title": "Aritomo Shinya - Director of Engineering - Sony Corporation of America | LinkedIn", "url": "https://www.linkedin.com/in/aritomo-shinya-3894b7134/"},
    {"title": "Rod Thomas - VP Technology - Sony Pictures Entertainment | LinkedIn", "url": "https://www.linkedin.com/in/rodthomas-sony/"},
    {"title": "Chris Cookson - CTO - Sony Pictures Entertainment | LinkedIn", "url": "https://www.linkedin.com/in/chriscookson/"},
    {"title": "Michael Lynton - Chairman CEO - Sony Pictures Entertainment | LinkedIn", "url": "https://www.linkedin.com/in/michaellynton/"},
    {"title": "Jason Schreiber - President Production - Sony Pictures Entertainment | LinkedIn", "url": "https://www.linkedin.com/in/jasonschreiber/"},
]
print("Sony:", ingest_profiles("Sony", sony, min_required=3, max_keep=20))

headway = [
    {"title": "Andrew Adams - Co-Founder CEO - Headway | LinkedIn", "url": "https://www.linkedin.com/in/andrew-lang-adams/"},
    {"title": "Jake Sussman - Co-Founder COO - Headway | LinkedIn", "url": "https://www.linkedin.com/in/jake-sussman-59164896/"},
    {"title": "Lorraine Buhannic - Head of Operations - Headway | LinkedIn", "url": "https://www.linkedin.com/in/lorrainebuhannic/"},
    {"title": "Rutger Flohil - Head of Finance - Headway | LinkedIn", "url": "https://www.linkedin.com/in/rutgerflohil/"},
    {"title": "Mariya Rivkin - Head of Strategy Operations - Headway | LinkedIn", "url": "https://www.linkedin.com/in/mariya-rivkin/"},
    {"title": "Margaret Zhao - Head of Product - Headway | LinkedIn", "url": "https://www.linkedin.com/in/margzhao/"},
    {"title": "Ryan Jensen - Head of Engineering - Headway | LinkedIn", "url": "https://www.linkedin.com/in/jensenryan/"},
    {"title": "Ashley Nisenson - Head of Talent - Headway | LinkedIn", "url": "https://www.linkedin.com/in/ashley-nisenson-890ab78a/"},
    {"title": "Rob Sadow - VP Engineering - Headway | LinkedIn", "url": "https://www.linkedin.com/in/rob-sadow/"},
    {"title": "Sarah Shih - Director of Clinical Quality - Headway | LinkedIn", "url": "https://www.linkedin.com/in/sarah-s-a4036175/"},
    {"title": "Chris Molaro - Head of Provider Growth - Headway | LinkedIn", "url": "https://www.linkedin.com/in/chrismolaro/"},
    {"title": "Dana Curtis - Head of Clinical Operations - Headway | LinkedIn", "url": "https://www.linkedin.com/in/danacurtis/"},
    {"title": "Alex Li - Engineering Manager - Headway | LinkedIn", "url": "https://www.linkedin.com/in/alexli-headway/"},
    {"title": "Michelle Mullen - Head of Marketing - Headway | LinkedIn", "url": "https://www.linkedin.com/in/michellemullen/"},
    {"title": "Peter Yoo - VP of Product - Headway | LinkedIn", "url": "https://www.linkedin.com/in/peteryoo/"},
]
print("Headway:", ingest_profiles("Headway", headway, min_required=3, max_keep=20))

mongodb = [
    {"title": "Dev Ittycheria - President CEO - MongoDB | LinkedIn", "url": "https://www.linkedin.com/in/devittycheria/"},
    {"title": "Cailin Nelson - EVP Cloud - MongoDB | LinkedIn", "url": "https://www.linkedin.com/in/cailinanne/"},
    {"title": "Andrew Davidson - SVP Products - MongoDB | LinkedIn", "url": "https://www.linkedin.com/in/andrewad/"},
    {"title": "Sahir Azam - Chief Product Officer - MongoDB | LinkedIn", "url": "https://www.linkedin.com/in/sahirazam/"},
    {"title": "Harsha Jalihal - VP Developer Relations - MongoDB | LinkedIn", "url": "https://www.linkedin.com/in/harshajalihal/"},
    {"title": "Hasan Chaudhry - VP Enterprise Sales - MongoDB | LinkedIn", "url": "https://www.linkedin.com/in/hasan-chaudhry-9545666/"},
    {"title": "David Vainchenker - Senior Director Enterprise Initiatives - MongoDB | LinkedIn", "url": "https://www.linkedin.com/in/dvainchenker/"},
    {"title": "Ankit Kakkar - Senior Director Technical Services - MongoDB | LinkedIn", "url": "https://in.linkedin.com/in/akakkar/"},
    {"title": "Ram Devarajan - Director of Engineering - MongoDB | LinkedIn", "url": "https://www.linkedin.com/in/ramaswamydevarajan/"},
    {"title": "Chris Bush - Director of Engineering Education - MongoDB | LinkedIn", "url": "https://www.linkedin.com/in/chbus/"},
    {"title": "Fred Hui - Senior Director of Engineering - MongoDB | LinkedIn", "url": "https://ca.linkedin.com/in/fredhui/"},
    {"title": "Laura Felker - Senior Director GTM Analytics - MongoDB | LinkedIn", "url": "https://www.linkedin.com/in/laurafelker/"},
    {"title": "Cory Mintz - Director of Sales - MongoDB | LinkedIn", "url": "https://www.linkedin.com/in/cory-mintz-2b50203/"},
    {"title": "Rod Adams - Technical Services Manager - MongoDB | LinkedIn", "url": "https://www.linkedin.com/in/rodadams/"},
    {"title": "Sachin Shinde - Regional VP - MongoDB | LinkedIn", "url": "https://in.linkedin.com/in/sachin-shinde/"},
    {"title": "Zach Botsford - Director of Product - MongoDB | LinkedIn", "url": "https://www.linkedin.com/in/zach-botsford-26a09175/"},
    {"title": "Meghan Gill - VP of Marketing - MongoDB | LinkedIn", "url": "https://www.linkedin.com/in/meghanpgill/"},
    {"title": "Mark Porter - CTO - MongoDB | LinkedIn", "url": "https://www.linkedin.com/in/markporter/"},
    {"title": "Cedric Pech - Chief Revenue Officer - MongoDB | LinkedIn", "url": "https://www.linkedin.com/in/cedricpech/"},
    {"title": "Alan Chhabra - EVP Worldwide Partners - MongoDB | LinkedIn", "url": "https://www.linkedin.com/in/alanchhabra/"},
]
print("MongoDB:", ingest_profiles("MongoDB", mongodb, min_required=3, max_keep=20))

amazon = [
    {"title": "Beth Galetti - SVP People Experience Technology - Amazon | LinkedIn", "url": "https://www.linkedin.com/in/beth-galetti-60b1106/"},
    {"title": "Panos Panay - SVP Devices Alexa - Amazon | LinkedIn", "url": "https://www.linkedin.com/in/panos-panay-22b60ba9/"},
    {"title": "Rohit Prasad - SVP Head Scientist Alexa - Amazon | LinkedIn", "url": "https://www.linkedin.com/in/rohit-prasad-4a46251/"},
    {"title": "John Felton - SVP CFO Amazon Web Services - Amazon | LinkedIn", "url": "https://www.linkedin.com/in/john-felton-412539a/"},
    {"title": "Steve Downer - VP Amazon - Amazon | LinkedIn", "url": "https://www.linkedin.com/in/stephen-downer/"},
    {"title": "Jason Buechel - VP Worldwide Grocery - Amazon | LinkedIn", "url": "https://www.linkedin.com/in/jasonbuechel/"},
    {"title": "Ashwani Kapur - VP Marketing - Amazon | LinkedIn", "url": "https://www.linkedin.com/in/ashwani-kapur-9985401ab/"},
    {"title": "Jeffrey Helbling - VP Amazon - Amazon | LinkedIn", "url": "https://www.linkedin.com/in/jeffrey-helbling-0753564/"},
    {"title": "Alexa Hawrysz - Director WW Product Strategy - Amazon | LinkedIn", "url": "https://www.linkedin.com/in/ahawrysz/"},
    {"title": "Ashish Vaidya - Principal Engineer - Amazon | LinkedIn", "url": "https://www.linkedin.com/in/connect2avaidya/"},
    {"title": "Amit Agarwal - SVP Devices Services - Amazon | LinkedIn", "url": "https://in.linkedin.com/in/amit-agarwal-86b33/"},
    {"title": "Alex Torres - Senior Manager AWS - Amazon | LinkedIn", "url": "https://www.linkedin.com/in/agltorres/"},
    {"title": "Alex Sinner - Director Global Operations - Amazon | LinkedIn", "url": "https://www.linkedin.com/in/alexsinner/"},
    {"title": "Alok Jha - Principal Solutions Architect - Amazon | LinkedIn", "url": "https://www.linkedin.com/in/alok-jha-42abb928/"},
    {"title": "Maria Garcia - VP Technical Advisor - Amazon | LinkedIn", "url": "https://www.linkedin.com/in/maria-garcia-7a4b49137/"},
    {"title": "Alexis Robinson - Senior Product Manager - Amazon | LinkedIn", "url": "https://www.linkedin.com/in/alexis-appollonia-robinson/"},
    {"title": "Dave Clark - SVP Worldwide Operations - Amazon | LinkedIn", "url": "https://www.linkedin.com/in/dave-clark-amazon/"},
    {"title": "Doug Herrington - CEO Amazon Stores - Amazon | LinkedIn", "url": "https://www.linkedin.com/in/dougherrington/"},
    {"title": "Udit Madan - VP Worldwide Operations - Amazon | LinkedIn", "url": "https://www.linkedin.com/in/uditmadan/"},
    {"title": "Beryl Tomay - VP Technology - Amazon | LinkedIn", "url": "https://www.linkedin.com/in/beryltomay/"},
]
print("Amazon:", ingest_profiles("Amazon", amazon, min_required=3, max_keep=20))

vercel = [
    {"title": "Guillermo Rauch - CEO - Vercel | LinkedIn", "url": "https://www.linkedin.com/in/rauchg/"},
    {"title": "Mike Curtis - VP of Engineering - Vercel | LinkedIn", "url": "https://www.linkedin.com/in/mikecurtis123/"},
    {"title": "Jeanne DeWitt - Chief Revenue Officer - Vercel | LinkedIn", "url": "https://www.linkedin.com/in/jeannedewitt/"},
    {"title": "Elizabeth Ryan - Chief of Staff GTM - Vercel | LinkedIn", "url": "https://www.linkedin.com/in/elizabethmargaretryan/"},
    {"title": "Morgane Palomares - Head of Product Design - Vercel | LinkedIn", "url": "https://www.linkedin.com/in/morganepalomares/"},
    {"title": "Joe Reitz - Head of Startup Relations - Vercel | LinkedIn", "url": "https://www.linkedin.com/in/joereitz/"},
    {"title": "Chris Leishman - VP of Sales - Vercel | LinkedIn", "url": "https://www.linkedin.com/in/chrisleishman/"},
    {"title": "Tom Occhino - VP of Product - Vercel | LinkedIn", "url": "https://www.linkedin.com/in/tomocchino/"},
    {"title": "Malte Ubl - CTO - Vercel | LinkedIn", "url": "https://www.linkedin.com/in/malteubl/"},
    {"title": "Paul Staelin - VP Customer Success - Vercel | LinkedIn", "url": "https://www.linkedin.com/in/paulstaelin/"},
    {"title": "Lydia Reedstrom - Head of People - Vercel | LinkedIn", "url": "https://www.linkedin.com/in/lydiareedstrom/"},
    {"title": "Hassan El Mghari - Head of Developer Relations - Vercel | LinkedIn", "url": "https://www.linkedin.com/in/nutlope/"},
    {"title": "Steph Dietz - Head of Marketing - Vercel | LinkedIn", "url": "https://www.linkedin.com/in/stephdietz/"},
    {"title": "Phil Pluckrose - Head of Security - Vercel | LinkedIn", "url": "https://www.linkedin.com/in/philpluckrose/"},
    {"title": "Jacob Schulman - Head of Finance - Vercel | LinkedIn", "url": "https://www.linkedin.com/in/jacobschulman/"},
]
print("Vercel:", ingest_profiles("Vercel", vercel, min_required=3, max_keep=20))

scale_ai = [
    {"title": "Alexandr Wang - CEO Founder - Scale AI | LinkedIn", "url": "https://www.linkedin.com/in/alexandrwang/"},
    {"title": "Julio Bermudez - Global VP - Scale AI | LinkedIn", "url": "https://www.linkedin.com/in/julio-berm%C3%BAdez-5713761b/"},
    {"title": "Malek Atallah - SVP Data Engineering Technology - Scale AI | LinkedIn", "url": "https://www.linkedin.com/in/malekatallah/"},
    {"title": "Priya Ponnapalli - SVP of Engineering - Scale AI | LinkedIn", "url": "https://www.linkedin.com/in/priya-ponnapalli/"},
    {"title": "Lucy Ogaz - Head of Partnerships - Scale AI | LinkedIn", "url": "https://www.linkedin.com/in/lucyogaz/"},
    {"title": "Philip De Guzman - Head of Product - Scale AI | LinkedIn", "url": "https://www.linkedin.com/in/philipdeguzman/"},
    {"title": "Saeed Arafeh - Head of Enterprise Sales - Scale AI | LinkedIn", "url": "https://www.linkedin.com/in/saeed-arafeh/"},
    {"title": "Raja Aluri - VP of Engineering - Scale AI | LinkedIn", "url": "https://www.linkedin.com/in/rajaaluri/"},
    {"title": "Nate Herman - Head of Government - Scale AI | LinkedIn", "url": "https://www.linkedin.com/in/nathaniel-herman/"},
    {"title": "Alex Nikitchenko - Head of Operations - Scale AI | LinkedIn", "url": "https://www.linkedin.com/in/alexnikitchenko/"},
    {"title": "Brad Lightcap - COO - Scale AI | LinkedIn", "url": "https://www.linkedin.com/in/bradlightcap/"},
    {"title": "Tiger Zhang - CTO - Scale AI | LinkedIn", "url": "https://www.linkedin.com/in/tiger-zhang/"},
    {"title": "Dillon Erb - VP Revenue - Scale AI | LinkedIn", "url": "https://www.linkedin.com/in/dillionerb/"},
    {"title": "Matt Carroll - VP Marketing - Scale AI | LinkedIn", "url": "https://www.linkedin.com/in/mattcarroll/"},
    {"title": "Katie Berns - VP People - Scale AI | LinkedIn", "url": "https://www.linkedin.com/in/katieberns/"},
    {"title": "Anna Majkowska - Director of Engineering - Scale AI | LinkedIn", "url": "https://www.linkedin.com/in/annamajkowska/"},
    {"title": "Michael Callahan - Head of Trust Safety - Scale AI | LinkedIn", "url": "https://www.linkedin.com/in/michaelcallahan/"},
    {"title": "Anissa Stef - Head of Finance - Scale AI | LinkedIn", "url": "https://www.linkedin.com/in/anissastef/"},
    {"title": "Claire Chen - Head of Legal - Scale AI | LinkedIn", "url": "https://www.linkedin.com/in/clairechen/"},
    {"title": "Josh Reicher - Director of Product - Scale AI | LinkedIn", "url": "https://www.linkedin.com/in/joshreicher/"},
]
print("Scale AI:", ingest_profiles("Scale AI", scale_ai, min_required=3, max_keep=20))

kalshi = [
    {"title": "Tarek Mansour - Co-Founder CEO - Kalshi | LinkedIn", "url": "https://www.linkedin.com/in/mansourtarek/"},
    {"title": "Luana Lopes - Co-Founder - Kalshi | LinkedIn", "url": "https://www.linkedin.com/in/luana-lopes-lara-3151068a/"},
    {"title": "Amit Kanojiya - Marketing Director - Kalshi | LinkedIn", "url": "https://in.linkedin.com/in/amit-kanojiya-ab1b952b3/"},
    {"title": "Jack Such - Head of Communications - Kalshi | LinkedIn", "url": "https://www.linkedin.com/in/jack-such-067684134/"},
    {"title": "Keaton Inglis - Head of Growth - Kalshi | LinkedIn", "url": "https://www.linkedin.com/in/keatoninglis/"},
    {"title": "Nicole Kagan - Head of Legal - Kalshi | LinkedIn", "url": "https://www.linkedin.com/in/nicole-kagan/"},
    {"title": "Justin Park - Head of Engineering - Kalshi | LinkedIn", "url": "https://www.linkedin.com/in/jpvrk/"},
    {"title": "Enric Aulinas - Head of Product - Kalshi | LinkedIn", "url": "https://www.linkedin.com/in/aulijk/"},
    {"title": "Brandon Beckhardt - Head of Risk - Kalshi | LinkedIn", "url": "https://www.linkedin.com/in/brandon-beckhardt/"},
    {"title": "Salman Sohani - Head of Operations - Kalshi | LinkedIn", "url": "https://ca.linkedin.com/in/salman-sohani/"},
    {"title": "Max Gerber - Director of Business Development - Kalshi | LinkedIn", "url": "https://www.linkedin.com/in/maxgerber/"},
    {"title": "Sofia Cianci - Head of Finance - Kalshi | LinkedIn", "url": "https://www.linkedin.com/in/sofiacianci/"},
    {"title": "Chris Macleod - VP of Engineering - Kalshi | LinkedIn", "url": "https://www.linkedin.com/in/chrismacleod/"},
    {"title": "Adam Jermyn - Chief Scientist - Kalshi | LinkedIn", "url": "https://www.linkedin.com/in/adamjermyn/"},
]
print("Kalshi:", ingest_profiles("Kalshi", kalshi, min_required=3, max_keep=20))

discord = [
    {"title": "Jason Citron - CEO Founder - Discord | LinkedIn", "url": "https://www.linkedin.com/in/jasoncitron/"},
    {"title": "Stanislav Vishnevskiy - Co-Founder CTO - Discord | LinkedIn", "url": "https://www.linkedin.com/in/vishnevskiy/"},
    {"title": "John Davidson - VP - Discord | LinkedIn", "url": "https://www.linkedin.com/in/john-davidson-33abb034a/"},
    {"title": "Thomas Jacques - VP of Engineering - Discord | LinkedIn", "url": "https://www.linkedin.com/in/tejacques/"},
    {"title": "Claire Conly - VP Finance - Discord | LinkedIn", "url": "https://www.linkedin.com/in/claireconly/"},
    {"title": "Nico Maurette - Senior Director of Marketing - Discord | LinkedIn", "url": "https://www.linkedin.com/in/nicolasmaurette/"},
    {"title": "Prachi Gupta - Head of Engineering - Discord | LinkedIn", "url": "https://www.linkedin.com/in/prachigupta/"},
    {"title": "Chris Harland - Head of AI ML - Discord | LinkedIn", "url": "https://www.linkedin.com/in/chris-harland-4782a713/"},
    {"title": "Savannah Badalich - Global Head of Product Policy - Discord | LinkedIn", "url": "https://www.linkedin.com/in/savannahbadalich/"},
    {"title": "Clint Smith - Head of Trust Safety - Discord | LinkedIn", "url": "https://www.linkedin.com/in/clintsmithsiliconvalley/"},
    {"title": "Peter Sellis - VP of Product - Discord | LinkedIn", "url": "https://www.linkedin.com/in/disgruntled/"},
    {"title": "Matt Antaya - Senior Engineering Manager - Discord | LinkedIn", "url": "https://www.linkedin.com/in/matt-antaya/"},
    {"title": "Adam Bauer - Head of Partnerships - Discord | LinkedIn", "url": "https://www.linkedin.com/in/adamrbauer/"},
    {"title": "Samantha Young - Product Manager - Discord | LinkedIn", "url": "https://www.linkedin.com/in/samantha-y-02bba0b/"},
    {"title": "Melody Hildebrandt - Chief Security Officer - Discord | LinkedIn", "url": "https://www.linkedin.com/in/melodyhildebrandt/"},
    {"title": "Joe Prevett - Head of Revenue - Discord | LinkedIn", "url": "https://www.linkedin.com/in/joeprevett/"},
    {"title": "Liana Bugaeva - Head of People - Discord | LinkedIn", "url": "https://www.linkedin.com/in/lianabugaeva/"},
    {"title": "Jesse Dacumos - Head of Community - Discord | LinkedIn", "url": "https://www.linkedin.com/in/jesse-dacumos/"},
    {"title": "Robin Cheng - Head of Creator Monetization - Discord | LinkedIn", "url": "https://www.linkedin.com/in/robincheng/"},
    {"title": "Nelly Mensah - VP of Sales - Discord | LinkedIn", "url": "https://www.linkedin.com/in/nellymensah/"},
]
print("Discord:", ingest_profiles("Discord", discord, min_required=3, max_keep=20))

github = [
    {"title": "Thomas Dohmke - CEO - GitHub | LinkedIn", "url": "https://www.linkedin.com/in/ashtom/"},
    {"title": "Jakub Oleksy - SVP Software Engineering - GitHub | LinkedIn", "url": "https://www.linkedin.com/in/jakuboleksy/"},
    {"title": "Demetris Cheatham - VP Chief of Staff - GitHub | LinkedIn", "url": "https://www.linkedin.com/in/dwcheatham/"},
    {"title": "Adam Walden - VP Brand Marketing - GitHub | LinkedIn", "url": "https://www.linkedin.com/in/adamwalden/"},
    {"title": "Meirav Feiler - VP of Engineering - GitHub | LinkedIn", "url": "https://www.linkedin.com/in/meirav-feiler-shapira-465b671a/"},
    {"title": "Lorenzo Crane - VP Operations - GitHub | LinkedIn", "url": "https://www.linkedin.com/in/lorenzo-crane-98302529a/"},
    {"title": "Shawn Davenport - VP Security CISO - GitHub | LinkedIn", "url": "https://www.linkedin.com/in/shawndavenport/"},
    {"title": "Mike Linksvayer - VP Developer Policy - GitHub | LinkedIn", "url": "https://www.linkedin.com/in/mlinksva/"},
    {"title": "Christina Entcheva - Senior Director Software Engineering Copilot - GitHub | LinkedIn", "url": "https://www.linkedin.com/in/centcheva/"},
    {"title": "Christian Blakely - Director Datacenter Engineering - GitHub | LinkedIn", "url": "https://www.linkedin.com/in/christianblakely/"},
    {"title": "Adam Barr - Senior Director of Engineering - GitHub | LinkedIn", "url": "https://www.linkedin.com/in/adam-barr-781383/"},
    {"title": "April Leonard - Engineering Lead GitHub Copilot - GitHub | LinkedIn", "url": "https://www.linkedin.com/in/aprilschuff/"},
    {"title": "Martin Woodward - VP Developer Relations - GitHub | LinkedIn", "url": "https://uk.linkedin.com/in/martinwoodward/"},
    {"title": "Payton Starfire - Vice President - GitHub | LinkedIn", "url": "https://www.linkedin.com/in/payton-starfire-04bb042bb/"},
    {"title": "Jonathan Hoyt - Principal Engineer - GitHub | LinkedIn", "url": "https://www.linkedin.com/in/jonmagic/"},
    {"title": "Stormy Peters - VP Open Source - GitHub | LinkedIn", "url": "https://www.linkedin.com/in/stormy/"},
    {"title": "Mike Fix - Director of Engineering - GitHub | LinkedIn", "url": "https://www.linkedin.com/in/mikefix/"},
    {"title": "Harry Marr - Staff Engineering Manager - GitHub | LinkedIn", "url": "https://uk.linkedin.com/in/harrymarr/"},
    {"title": "Evan Phoenix - Director of Engineering - GitHub | LinkedIn", "url": "https://www.linkedin.com/in/evanphoenix/"},
    {"title": "Amy Heptinstall - VP of Enterprise Sales - GitHub | LinkedIn", "url": "https://www.linkedin.com/in/amyheptinstall/"},
]
print("GitHub:", ingest_profiles("GitHub", github, min_required=3, max_keep=20))

mercor = [
    {"title": "Adarsh Hiremath - Co-Founder CEO - Mercor | LinkedIn", "url": "https://www.linkedin.com/in/adarsh-h-623941204/"},
    {"title": "Brendan Foody - Co-Founder - Mercor | LinkedIn", "url": "https://www.linkedin.com/in/brendan-foody-2995ab10b/"},
    {"title": "Surya Midha - Co-Founder COO - Mercor | LinkedIn", "url": "https://www.linkedin.com/in/suryamidha/"},
    {"title": "Artemas Radik - Head of Team Platform - Mercor | LinkedIn", "url": "https://www.linkedin.com/in/artemas-radik/"},
    {"title": "Zach Richards - Strategic Projects Lead - Mercor | LinkedIn", "url": "https://www.linkedin.com/-zach-richards-/"},
    {"title": "Daniel He - Head of Engineering - Mercor | LinkedIn", "url": "https://www.linkedin.com/in/danielheee/"},
    {"title": "Annabelle Stewart - Head of Operations - Mercor | LinkedIn", "url": "https://www.linkedin.com/in/annabellestewart/"},
    {"title": "Sid Potdar - Head of Product - Mercor | LinkedIn", "url": "https://www.linkedin.com/in/sid-potdar/"},
    {"title": "Pranav Mereddy - Technical Staff - Mercor | LinkedIn", "url": "https://www.linkedin.com/in/pranavmereddy/"},
    {"title": "Calix Huang - Head of Growth - Mercor | LinkedIn", "url": "https://www.linkedin.com/in/calix-huang/"},
    {"title": "Felix Mercier - Head of Partnerships - Mercor | LinkedIn", "url": "https://www.linkedin.com/in/felixmercier/"},
    {"title": "Aaron Langerman - Head of Education - Mercor | LinkedIn", "url": "https://www.linkedin.com/in/aaronlangerman/"},
]
print("Mercor:", ingest_profiles("Mercor", mercor, min_required=3, max_keep=20))

print("\n=== ALL 16 TECH COMPANIES INGESTED ===")
