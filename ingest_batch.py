from linkedin_ingest import ingest_profiles

# New York Life Insurance
nyl = [
    {"title": "Eric Feldstein - Executive Vice President Chief Financial Officer - New York Life Insurance | LinkedIn", "url": "https://www.linkedin.com/in/ericfeldstein1"},
    {"title": "Richard Murphy - Corporate Vice President - New York Life | LinkedIn", "url": "https://www.linkedin.com/in/richard-murphy-1187b58"},
    {"title": "Stacey Simbal - Corporate Vice President - New York Life Insurance | LinkedIn", "url": "https://www.linkedin.com/in/stacey-simbal-65494631"},
    {"title": "Brian Mannix - Corporate Vice President - New York Life | LinkedIn", "url": "https://www.linkedin.com/in/brian-mannix-a5ba3215"},
    {"title": "Dan Rice - Corporate Vice President - New York Life | LinkedIn", "url": "https://www.linkedin.com/in/dan-rice-43a60a7"},
    {"title": "Joe Zufall - Corporate Vice President - New York Life Insurance | LinkedIn", "url": "https://www.linkedin.com/in/joe-zufall-8a493950"},
    {"title": "Maura Colleary - Senior Vice President Chief Procurement Officer Finance - New York Life Insurance | LinkedIn", "url": "https://www.linkedin.com/in/maura-colleary-8416a713"},
    {"title": "Amy Hu - Senior Vice President Insurance Solutions - New York Life Insurance | LinkedIn", "url": "https://www.linkedin.com/in/amyhu2"},
    {"title": "Vikas Sharma - Senior Vice President - New York Life Insurance | LinkedIn", "url": "https://www.linkedin.com/in/vikas-sharma-14ba21a"},
    {"title": "Richard Severo - Corporate Vice President - New York Life Insurance | LinkedIn", "url": "https://www.linkedin.com/in/richard-severo-50b7834a"},
]
n = ingest_profiles("New York Life Insurance", nyl)
print(f"New York Life Insurance: {n}")

# Northwestern Mutual
nm = [
    {"title": "Tim Gerend - Managing Director - Northwestern Mutual | LinkedIn", "url": "https://www.linkedin.com/in/tim-gerend-67753425"},
    {"title": "Clarissa Ortiz - Vice President Chief of Staff - Northwestern Mutual | LinkedIn", "url": "https://www.linkedin.com/in/clarissa-ortiz-4457056"},
    {"title": "Dave Simbro - Senior Vice President - Northwestern Mutual | LinkedIn", "url": "https://www.linkedin.com/in/dave-simbro-21301810"},
    {"title": "Kelly Culler - Executive Vice President Chief People Officer - Northwestern Mutual | LinkedIn", "url": "https://www.linkedin.com/in/kellyiculler"},
    {"title": "Archana Lamoureux - Vice President Head of Corporate Digital Solutions - Northwestern Mutual | LinkedIn", "url": "https://www.linkedin.com/in/archanalamoureux"},
    {"title": "Mindi Sinclair - Chief Operating Officer - Northwestern Mutual | LinkedIn", "url": "https://www.linkedin.com/in/mindi-sinclair-51084512"},
    {"title": "Ray Manista - Senior Vice President - Northwestern Mutual | LinkedIn", "url": "https://www.linkedin.com/in/ray-manista-8ba40626"},
    {"title": "John Crawford - Managing Director - Northwestern Mutual | LinkedIn", "url": "https://www.linkedin.com/in/john-crawford-646a18"},
    {"title": "Timothy Collins - Managing Director - Northwestern Mutual | LinkedIn", "url": "https://www.linkedin.com/in/timothy-collins-8687b515"},
]
n = ingest_profiles("Northwestern Mutual", nm)
print(f"Northwestern Mutual: {n}")

# MetLife
metlife = [
    {"title": "Michel A. Khalaf - President Chief Executive Officer - MetLife | LinkedIn", "url": "https://www.linkedin.com/in/michel-a-khalaf"},
    {"title": "Scott Pavlak - Senior Vice President Managing Director - MetLife Investment Management | LinkedIn", "url": "https://www.linkedin.com/in/scott-pavlak-a0543721"},
    {"title": "Lori Akers - Vice President Finance Technology Solutions - MetLife | LinkedIn", "url": "https://www.linkedin.com/in/lori-akers-3401835"},
    {"title": "Shurawl Sibblies - Senior Vice President - MetLife | LinkedIn", "url": "https://www.linkedin.com/in/shurawlsibblies"},
    {"title": "Bill O'Donnell - Executive Vice President Chief Financial Officer MetLife U.S. | LinkedIn", "url": "https://www.linkedin.com/in/bill-o-donnell-6b681a1b"},
    {"title": "Mike Giovanni - Senior Director Vice President - MetLife Investment Management | LinkedIn", "url": "https://www.linkedin.com/in/mike-giovanni-9a698b28"},
    {"title": "Sean Ritter - Managing Director - MetLife Middle Market Private Capital | LinkedIn", "url": "https://www.linkedin.com/in/sean-ritter-236a9b4"},
    {"title": "Thomas Ho - Vice President - MetLife Private Capital Investor | LinkedIn", "url": "https://www.linkedin.com/in/thomas-ho-b83430"},
    {"title": "John McCallion - Senior Vice President - MetLife | LinkedIn", "url": "https://www.linkedin.com/in/john-mccallion-324b21144"},
    {"title": "John Hall - Executive Vice President Treasurer - MetLife | LinkedIn", "url": "https://www.linkedin.com/in/john-hall-a0a54614"},
]
n = ingest_profiles("MetLife", metlife)
print(f"MetLife: {n}")

# Allstate
allstate = [
    {"title": "Fred Hansen - Senior Vice President Managing Director - Allstate | LinkedIn", "url": "https://www.linkedin.com/in/fred-hansen-20a9a5210"},
    {"title": "Andrea Carter - Executive Vice President Chief Human Resources Officer - Allstate | LinkedIn", "url": "https://www.linkedin.com/in/andrea-carter-640b254"},
    {"title": "Jerry Zimmerman - Legal Counsel Advisor - Allstate | LinkedIn", "url": "https://www.linkedin.com/in/gerald-zimmerman120466"},
    {"title": "Larry Sedillo - Field Senior Vice President - Allstate | LinkedIn", "url": "https://www.linkedin.com/in/larry-sedillo-13137119"},
    {"title": "Gerard Gregoire - Vice President Associate General Counsel Law Regulation - Allstate | LinkedIn", "url": "https://www.linkedin.com/in/gerard-gregoire-24689263"},
    {"title": "Jordan Canter - Vice President Head of Federal Affairs - Allstate | LinkedIn", "url": "https://www.linkedin.com/in/jordan-canter-9150173a"},
    {"title": "Jess Merten - President Property-Liability - Allstate | LinkedIn", "url": "https://www.linkedin.com/in/jess-merten-44297119"},
    {"title": "Kristine Stelzer - Vice President Corporate Brand - Allstate | LinkedIn", "url": "https://www.linkedin.com/in/kristine-stelzer-97411698"},
    {"title": "Mario Rizzo - Chief Operating Officer - Allstate | LinkedIn", "url": "https://www.linkedin.com/in/mario-rizzo-b2787bb"},
    {"title": "Mike Demetre - Senior Vice President General Manager - Allstate | LinkedIn", "url": "https://www.linkedin.com/in/mike-demetre-5b58894"},
]
n = ingest_profiles("Allstate", allstate)
print(f"Allstate: {n}")

# BlackRock
blackrock = [
    {"title": "Christopher Brown - Managing Director - BlackRock | LinkedIn", "url": "https://www.linkedin.com/in/christopher-brown-03a27a9"},
    {"title": "Vince Russo - Vice President - BlackRock | LinkedIn", "url": "https://www.linkedin.com/in/vrusso33"},
    {"title": "Larry Fink - Chairman Chief Executive Officer - BlackRock | LinkedIn", "url": "https://www.linkedin.com/in/laurencefink"},
    {"title": "Gurwin Singh Ahuja - Vice President - BlackRock | LinkedIn", "url": "https://www.linkedin.com/in/gurwin-singh-ahuja-a1158542"},
    {"title": "Catherine Peter - Senior Vice President - BlackRock | LinkedIn", "url": "https://www.linkedin.com/in/catherine-peter-28a22710"},
    {"title": "Abhi Gupta - Vice President - BlackRock | LinkedIn", "url": "https://www.linkedin.com/in/abhi-gupta-4a6b51127"},
    {"title": "Rick Rieder - Senior Managing Director Chief Investment Officer Global Fixed Income - BlackRock | LinkedIn", "url": "https://www.linkedin.com/in/rick-rieder-b64336249"},
    {"title": "Abhishek Patel - Vice President - BlackRock | LinkedIn", "url": "https://www.linkedin.com/in/apatel95"},
    {"title": "Alexandra Eldemir - Managing Director - BlackRock | LinkedIn", "url": "https://www.linkedin.com/in/alexandra-eldemir-4350966b"},
    {"title": "Jennifer O'Neil - Managing Director - BlackRock | LinkedIn", "url": "https://www.linkedin.com/in/jennifer-o-neil-ab42014"},
]
n = ingest_profiles("BlackRock", blackrock)
print(f"BlackRock: {n}")

# Charter Communications
charter = [
    {"title": "Jamal Haughton - Executive Vice President General Counsel - Charter Communications | LinkedIn", "url": "https://www.linkedin.com/in/jamal-haughton-484a9a21"},
    {"title": "Taylor Vice - Senior Director Government Affairs - Charter Communications | LinkedIn", "url": "https://www.linkedin.com/in/taylorvice"},
    {"title": "Joseph Varello - Vice President Sales - Charter Spectrum | LinkedIn", "url": "https://www.linkedin.com/in/joevarello"},
    {"title": "Larry Christopher - Vice President Associate General Counsel Litigation - Charter Communications | LinkedIn", "url": "https://www.linkedin.com/in/larry-christopher-32b99a34"},
    {"title": "Jeff Jarecke - Senior Director MDU Sales - Charter Communications | LinkedIn", "url": "https://www.linkedin.com/in/jeff-jarecke-781b369"},
    {"title": "Cody Harrison - Vice President Associate General Counsel - Charter Communications | LinkedIn", "url": "https://www.linkedin.com/in/cody-harrison-b92356a4"},
    {"title": "Kara Bush - Associate Vice President Government Affairs - Charter Communications | LinkedIn", "url": "https://www.linkedin.com/in/kara-bush-584bb818"},
    {"title": "Rick Dykhouse - Vice President Senior Counsel - Charter Communications | LinkedIn", "url": "https://www.linkedin.com/in/rick-dykhouse-3395096"},
    {"title": "Whitney O'Neill - Vice President Government Affairs - Charter Communications | LinkedIn", "url": "https://www.linkedin.com/in/whitney-o-neill-3326ba40"},
]
n = ingest_profiles("Charter Communications", charter)
print(f"Charter Communications: {n}")

# Comcast
comcast = [
    {"title": "Cathy Traczek - Senior Vice President - Comcast Cable | LinkedIn", "url": "https://www.linkedin.com/in/cathytraczek"},
    {"title": "Bill Ferry - Senior Director - Comcast | LinkedIn", "url": "https://www.linkedin.com/in/bill-ferry-0ab039260"},
    {"title": "David Egan - Vice President Comcast Business Freedom Region | LinkedIn", "url": "https://www.linkedin.com/in/davidegancomcast"},
    {"title": "Cory Harriger - Vice President Customer Experience Strategy Operations | LinkedIn", "url": "https://www.linkedin.com/in/cory-harriger-50980b8"},
    {"title": "Anthony Biggs - Regional Vice President Technical Operations - Comcast | LinkedIn", "url": "https://www.linkedin.com/in/anthony-biggs-38b50599"},
    {"title": "Tracy Pitcher - Senior Vice President Comcast Business | LinkedIn", "url": "https://www.linkedin.com/in/tracy-pitcher-6baa645"},
    {"title": "Mindy Kramer - Vice President Public Relations Florida Region - Comcast Cable | LinkedIn", "url": "https://www.linkedin.com/in/mindy-kramer-58913b4"},
    {"title": "Leo Munoz - Executive Director - Comcast | LinkedIn", "url": "https://www.linkedin.com/in/leo-munoz-60a3695"},
    {"title": "Marianne Bichsel - Vice President External Affairs - Comcast | LinkedIn", "url": "https://www.linkedin.com/in/mariannebichsel"},
    {"title": "Nick Kask - Vice President Finance Operations - Comcast | LinkedIn", "url": "https://www.linkedin.com/in/nicholaskask"},
]
n = ingest_profiles("Comcast", comcast)
print(f"Comcast: {n}")

# T-Mobile
tmobile = [
    {"title": "David M. Bezzant - Vice President Public Sector - T-Mobile | LinkedIn", "url": "https://www.linkedin.com/in/davidbezzant"},
    {"title": "John Stevens - Senior Vice President - T-Mobile | LinkedIn", "url": "https://www.linkedin.com/in/john-stevens-94b26b7"},
    {"title": "Salim Kouidri - Senior Vice President Technology - T-Mobile US | LinkedIn", "url": "https://www.linkedin.com/in/salim-kouidri-057301"},
    {"title": "Wanny M. - Vice President T-Mobile Southeast | LinkedIn", "url": "https://www.linkedin.com/in/wannymanasse"},
    {"title": "Kimberly Wyman - Vice President Customer Care - T-Mobile | LinkedIn", "url": "https://www.linkedin.com/in/kimberly-wyman-5b64629"},
    {"title": "Jon Freier - Chief Operating Officer - T-Mobile US | LinkedIn", "url": "https://www.linkedin.com/in/jonfreier"},
    {"title": "Peter Osvaldik - Vice President Supply Chain - T-Mobile | LinkedIn", "url": "https://www.linkedin.com/in/peter-osvaldik-3887394"},
    {"title": "Susan Loosmore - Executive Vice President - T-Mobile | LinkedIn", "url": "https://www.linkedin.com/in/susan-loosmore-71390859"},
    {"title": "Matt Robertson - Vice President T-Mobile For Business | LinkedIn", "url": "https://www.linkedin.com/in/matt-robertson-821998139"},
    {"title": "Deeanne King - Executive Vice President Chief Human Resources Officer - T-Mobile | LinkedIn", "url": "https://www.linkedin.com/in/deeanne-king-3b8073a"},
]
n = ingest_profiles("T-Mobile", tmobile)
print(f"T-Mobile: {n}")

print("\n=== ALL REMAINING 8 COMPANIES INGESTED ===")
