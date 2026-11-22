"""Mylene Bio, rules update 2026-11-22 (Fable 5.2).
Takes the CURRENT Bio body (cur.html, pulled from the review page) and runs the new rules through it:
E1 ending as the last two cards, base-flow order (openers before songs), three folds
(Mylene Hart / The Underground / The Regular), first-person text, coloured names + key,
2 songs showing, creators inside the author's note. The Red Bloom boss fight is not touched.

    python3 build.py            -> bio.html (preview, local img/) + bio-janitor.html (hosted ending assets) + index.html (viewer)
"""
import re, sys
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString

HERE = Path(__file__).parent
sys.path.insert(0, '/mnt/project-files/universal-buttons/ending-final')
sys.path.insert(0, '/mnt/project-files/universal-buttons/banners-r2')
sys.path.insert(0, '/mnt/project-files/bio-viewer')
from ending import ending_html, HOSTED

AMBER = '#ffb35c'; ROSE = '#ff7aa8'; RED = '#e0435a'; CREAM = '#f4ebe2'
NAMES = {'Mylene': AMBER, 'Kira': '#ff6f3c', 'Amaya': '#ff9ad5', 'Millie': '#c88cff'}
OUTLINE = '2px 0 0 #0b090c,-2px 0 0 #0b090c,0 2px 0 #0b090c,0 -2px 0 #0b090c,2px 2px 0 #0b090c,-2px -2px 0 #0b090c,2px -2px 0 #0b090c,-2px 2px 0 #0b090c'


def frag(html):
    return BeautifulSoup(html, 'html.parser')


def kids(e):
    return e.find_all(recursive=False)


def chev(c):
    return (f'<span data-chev="1" style="flex:0 0 auto;display:inline-flex;align-items:center;justify-content:center;width:1.86em;height:1.86em;border-radius:.29em;background:#07050b;box-shadow:0 0 0 2px {c},0 0 .86em {c}88;vertical-align:middle;">'
            f'<span style="display:block;width:.57em;height:.57em;margin-top:-.21em;border-right:.21em solid {c};border-bottom:.21em solid {c};transform:rotate(45deg);"></span></span>')


def plaid(c):
    g = f'#0000 0 2.43em,{c}38 2.43em 3.57em,#0000 3.57em 4.43em,#ffffff10 4.43em 4.57em,#0000 4.57em 6em'
    return (f'margin:0 0 1.57em;border-radius:1.43em;background:repeating-linear-gradient(90deg,{g}),repeating-linear-gradient(0deg,{g}),'
            'repeating-linear-gradient(90deg,#0000 0 .43em,#00000022 .43em .5em),#231c22;box-shadow:0 0 0 .21em #000,0 0 0 .36em #cfc8d255,0 1em 2.14em #000c;padding:1em .86em 1.14em;overflow:hidden;')


STRIP = ('<div style="line-height:0;container-type:inline-size;margin:0 auto;max-width:31.43em;"><img src="img/rose-strip.webp" alt="roses · LuvBytes" '
         'style="display:block;width:100cqw;height:auto;filter:drop-shadow(0 .21em 0 #000);"></div>')


def fold_summary(title, sub, c, rot, plate=None):
    return ('<summary style="list-style:none;cursor:pointer;display:flex;align-items:center;gap:.57em;padding:.14em .14em .14em .29em;">'
            '<span style="flex:1 1 auto;min-width:0;text-align:center;">'
            + (f'<img src="{plate}" alt="{title} · LuvBytes" style="display:block;width:min(100%,15em);height:auto;margin:0 auto;filter:drop-shadow(0 .2em .3em #000a);">' if plate else
               f'<span style="display:block;font-family:\'Berkshire Swash\',Georgia,serif;font-size:1.75em;line-height:1.1;color:{CREAM};transform:rotate({rot}deg);text-shadow:{OUTLINE},.1em .1em 0 {c};">{title}</span>') +
            f'<span style="display:block;font:700 .6em/1.3 Jura,sans-serif;letter-spacing:.18em;color:{c};margin-top:.5em;">{sub}</span></span>'
            + chev(c) + '</summary>')


def fold_board(colour, title, sub, c, rot, body_nodes, plate=None):
    """plaid board, rose strips top and bottom, the middle is one fold"""
    b = frag(f'<div style="{plaid(colour)}">{STRIP}<div style="padding:.86em 0 .71em;"><details>{fold_summary(title, sub, c, rot, plate)}'
             '<div data-foldbody="1" style="animation:sonner-fade-in .4s ease-out both;margin-top:1em;"></div></details></div>' + STRIP + '</div>').div
    body = b.find(attrs={'data-foldbody': '1'})
    del body['data-foldbody']
    for n in body_nodes:
        body.append(n)
    return b


def set_text(el, text):
    el.clear(); el.append(NavigableString(text))


def find_text(root, needle, name=None):
    for t in root.find_all(name or True):
        if t.string and needle in t.string and not t.find(True):
            return t
    raise KeyError(needle)


def build(base):
    soup = BeautifulSoup((HERE / 'cur.html').read_text(encoding='utf-8'), 'html.parser')
    for sp in soup.find_all('span', class_='css-fbq013'):
        sp.unwrap()
    card_p = soup.find('p', recursive=False)
    outer = soup.find_all('div', recursive=False)[0]
    inner = outer.find('div')
    top, a_media, songs, a_open, openers, boss, sandbox, note, creators, banners, follow, a_end, foot = kids(inner)
    hero, jumpbox, about, girls = kids(top)
    # Viki 2026-11-22 19:02: Red Bloom keeps the portrait card with the HP bar and the five lines, then goes straight to the ending
    # picture ("Come on. Show me something unforgettable." / SIGNAL RESTORED). The scar, the three tests and the four moves are out.
    bmain = kids(boss)[2]
    bk = kids(bmain)
    kids(kids(bk[4])[1])[1].decompose()          # "Three little tests, sweetheart..." line
    for n in bk[5:8]:
        assert any(w in n.get_text() for w in ('THE SCAR', 'THREE LITTLE TESTS', 'YOUR MOVE')), n.get_text()[:40]
        n.decompose()
    boss_html = str(boss)

    # ------------------------------------------------------------ card hook: lettering baked under the card (Viki 2026-11-22, the Lupa way)
    card_p.clear()
    card_p.append(frag('<img src="img/mylene-card-hook.webp" alt="Mylene · Door\'s locked, sweetheart. Come sit closer~ · LuvBytes" style="width:100%;max-width:360px;border-radius:5%">'))

    # ------------------------------------------------------------ opener cards: chevron + dropdown with more info
    OPEN = [
        ('Heroic Entrance', '11:42 PM | Friday, autumn | The Underground | 19°C', 'A pushy stranger crowds my favourite regular. I cut in, then check who needs a drink.', '',
         ['Thank me for the rescue', 'Rate my heroic entrance', 'Take the drink and stay']),
        ('Rooftop After the Set', '12:16 AM | Saturday, autumn | the bar rooftop | 9°C', 'After my set I bring somebody special up to the quiet roof and wrap my jacket around them.', '',
         ['Give me honest feedback on the set', 'Ask why I kept finding one face', 'Keep my jacket, lean closer']),
        ('Bonfire on the Coast', '8:03 PM | Saturday, summer | Oregon coast | 17°C', 'Band bonfire on the beach. I pat the blanket beside me and hold out a cinnamon drink.', 'Kira, Amaya, Millie',
         ['Sit with me and take the mug', 'Tell me something true', 'Join Kira, Amaya or Millie']),
        ('Snowed In', '10:37 PM | Friday, winter | the shared house | 22°C', 'Movie night with snow at the windows. I lift my blanket and call somebody over to get warm.', 'Kira, Amaya, Millie',
         ['Crawl under my blanket', 'Make me come and carry you', 'Stay put and see what I do']),
        ('Dessert Upstairs', '1:18 AM | Saturday, spring | my kitchen above the bar | 20°C', "After closing I'm on my kitchen counter in an open robe, and dessert is me.", '',
         ['Watch me finish', 'Lick up the sauce', 'Ask me for an instruction']),
        ('Tour Bus Morning', '9:26 AM | Tuesday, summer | the tour bus | 21°C', "A slow morning on the parked bus. My girls are already busy with each other, and I'm watching over coffee.", 'Kira, Amaya, Millie',
         ['Help Millie', 'Help Amaya with Kira', 'Enjoy the show with me']),
        ('Cannon Beach', '3:17 PM | Sunday, summer | Cannon Beach, Oregon | 18°C', 'The girls tease Millie about hiding her curves. I lean over and offer a choice.', 'Kira, Amaya, Millie',
         ['Pick boobs', 'Pick ass', 'Join in teasing Millie']),
        ('Burn It Away', '12:48 AM | Saturday, autumn | my bedroom above the bar | 20°C', 'A nightmare shift. I bring it upstairs, wound up and nowhere near done.', '',
         ['Start over with me', 'Tell me how to finish', 'Take a deep breath, hold on']),
    ]
    og = find_text(openers, 'Heroic Entrance', 'div').parent.parent.parent
    assert '5.93em' in og['style']; og['style'] = og['style'].replace('5.93em', '7.2em')   # four across on PC, two on phones
    for i, (title, header, setup, cast, acts) in enumerate(OPEN):
        c = AMBER if i < 4 else ROSE
        tdiv = find_text(openers, title, 'div')
        pad = tdiv.parent
        li = ''.join(f'<div style="display:flex;gap:.4em;margin-top:.3em;"><span style="flex:0 0 auto;color:{c};font-weight:700;">›</span><span style="min-width:0;">{a}</span></div>' for a in acts)
        castl = f'<div style="margin-top:.5em;font:700 .78em/1.4 Jura,sans-serif;letter-spacing:.1em;color:#cfc8d2;">WITH <span style="font:600 1.1em/1.4 Lexend,system-ui,sans-serif;letter-spacing:0;">{cast}</span></div>' if cast else ''
        pad.append(frag(
            '<details style="margin-top:.57em;padding-top:.5em;border-top:1px solid #ffffff1c;">'
            '<summary style="list-style:none;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:.5em;">'
            f'<span style="font:700 .6em/1.3 Jura,sans-serif;letter-spacing:.18em;color:{c};">MORE</span><span style="font-size:.72em;line-height:0;">{chev(c)}</span></summary>'
            '<div style="animation:sonner-fade-in .4s ease-out both;margin-top:.57em;text-align:left;font:300 .8em/1.45 Lexend,system-ui,sans-serif;color:#e9dfe4;">'
            f'<div style="font:700 .74em/1.5 Jura,sans-serif;letter-spacing:.08em;color:{c};">{header}</div>'
            f'<div style="margin-top:.4em;">{setup}</div>{castl}<div style="margin-top:.5em;">{li}</div>'
            '<div style="margin-top:.5em;font:italic 400 1.1em/1.4 \'Crimson Text\',Georgia,serif;color:#f4ebe2;">Or do whatever you want.</div></div></details>'))

    # ------------------------------------------------------------ hero pitch (first person)
    set_text(hero.find('p'), "The Underground is my moms' bar, down a flight of stairs in Portland. I pour until the last song, then I get up on stage and sing it. "
             "A certain regular keeps taking the same stool. I noticed early, sweetheart, and I have been keeping an eye on that seat ever since.")

    # ------------------------------------------------------------ jump box
    set_text(jumpbox.find('p'), "I'm a soft dom who feeds people first. Four soft nights, four after hours, and one boss fight where the page breaks. Any gender, any POV.")
    for old, new in (('The openers', 'Skip to the openings'), ('Her songs & gallery', 'Music & Gallery'), ('skip to the end and start your chat', 'Jump to the end')):
        set_text(find_text(jumpbox, old, 'span'), new)
    labs = jumpbox.find_all('label')
    labs[0]['style'] = labs[0]['style'].replace('flex:1 1 calc(50% - .43em)', 'flex:1 1 100%')
    labs[2]['style'] = labs[2]['style'].replace('flex:1 1 100%', 'flex:1 1 calc(50% - .43em)').replace('min-width:0', 'min-width:6.86em')
    for l in labs[1:]:
        t = l.find('span').find('span') or l.find('span'); t['style'] = t['style'].replace('.95em', '.86em')
    appnote = jumpbox.find(attrs={'data-appnote': '1'})
    appnote.insert_after(frag('<div style="text-align:center;font-family:Lexend,Arial,sans-serif;font-size:.62em;color:#a99bb8;margin-top:3px;">Click any image to enlarge it ♡</div>'))
    key = ''.join(f'<span style="display:inline-block;margin:0 .5em;white-space:nowrap;"><span style="display:inline-block;width:.6em;height:.6em;border-radius:50%;background:{c};margin-right:.36em;"></span>'
                  f'<b style="color:{c};">{n}</b></span>' for n, c in NAMES.items())
    jumpbox.append(frag('<div style="margin-top:.86em;padding-top:.71em;border-top:1px solid #ffffff1c;text-align:center;font:600 .72em/1.7 Lexend,system-ui,sans-serif;">'
                        f'<span style="font:700 .86em/1 Jura,sans-serif;letter-spacing:.2em;color:#cfc8d2;margin-right:.3em;">NAMES</span>{key}</div>'))

    # ------------------------------------------------------------ fold 1: Mylene Hart
    a_strip1, a_pad, a_strip2 = kids(about)
    a_title, a_grid1, a_grid2, a_more = kids(a_pad)
    set_text(a_grid1.find('p'), "I sing for Black Sugar and pour at my moms' bar. I hum jazz while I cook, and I fix collars before I notice my hands moved. "
             "People lean on me before they realise they stepped closer. Everybody falls into me, sweetheart. Nobody has thought to offer me the same. Yet.")
    set_text(find_text(a_grid1, "5'9", 'span'), '5′9″ · 175 CM')
    set_text(find_text(a_grid2, 'unkind to her girls', 'span'), 'cruelty, and anyone who is unkind to my girls')
    set_text(find_text(a_grid2, 'nose ring', 'span'), "I fiddle with my nose ring when I'm nervous")
    right = kids(a_grid2)[1]
    quote_card, you_her = kids(right)
    you_her.extract()
    more_body = kids(a_more)[1]          # the div under the summary
    cards, wants = kids(more_body)
    set_text(find_text(cards, 'simmering'), 'Something is always simmering on my stove for whoever needs it.')
    lab = find_text(cards, 'Her jacket').find_previous_sibling('div')
    lab.contents[-1].replace_with("WHEN IT'S COLD")
    set_text(find_text(cards, 'Her jacket'), "My jacket is already on somebody's shoulders. Guess whose.")
    lab = find_text(cards, 'What she is afraid').find_previous_sibling('div')
    lab.contents[-1].replace_with("I WON'T SAY")
    set_text(find_text(cards, 'What she is afraid'), 'What scares me when the bar is empty. Somebody would have to notice first.')
    set_text(find_text(wants, 'SHE WANTS'), 'I WANT')
    set_text(find_text(wants, 'Her people safe'), 'My people safe, fed and warm. And someone who stays when I stop being the shelter.')
    wants.extract(); wants['style'] = wants['style'].replace('margin-top:.71em;', '')
    right.append(wants)
    cards.extract(); cards['style'] = cards['style'].replace('14.29em', '9.5em') + 'margin-top:1.14em;'
    a_more.decompose(); a_title.decompose()
    f1 = fold_board('#3b1d33', 'Mylene Hart', 'TAP TO MEET HER', AMBER, -2, [a_grid1.extract(), a_grid2.extract(), cards], plate='img/mylene-hart-plate.webp')
    about.replace_with(f1)

    # ------------------------------------------------------------ fold 2: The Underground (world + her girls)
    g_strip1, g_pad, g_strip2 = kids(girls)
    g_title, g_card, g_tag = kids(g_pad)
    set_text(find_text(g_card, 'Mylene keeps her fed'), 'Sharp edges, soft heart. I keep her fed and out of fights. Mostly.')
    set_text(find_text(g_card, 'The smallest and the oldest'), 'The smallest and the oldest of us. A pastel idol until she sits at the kit.')
    set_text(find_text(g_card, 'Glued to her phone'), 'Glued to her phone, runs our visuals, never misses a shot.')
    for im in g_card.find_all('img'):       # side characters: small 1:1 picture, the click opens the whole portrait
        im['style'] += 'aspect-ratio:1/1;object-fit:cover;object-position:50% 14%;'
        fr = im.find_parent('div').find_parent('div')
        fr['style'] = fr['style'].replace('flex:0 0 38%;max-width:10.71em', 'flex:0 0 34%;max-width:8.2em')
    gg = g_card.find('div'); gg['style'] = gg['style'].replace('15.71em', '13.5em')
    place = frag('<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,15em),1fr));gap:0;border-radius:1em;background:#0d0b0e;box-shadow:0 0 0 2px #000,inset 0 0 0 1px #ffb35c55;overflow:hidden;align-items:center;">'
                 '<div style="min-width:0;line-height:0;container-type:inline-size;background:#0d0b0e;"><img src="img/bar.webp" alt="The Underground bar · LuvBytes" style="display:block;width:100cqw;height:auto;"></div>'
                 '<div style="min-width:0;padding:.86em 1em 1em;"><div style="font:700 .66em/1.3 Jura,sans-serif;letter-spacing:.16em;color:#ffb35c;">THE BAR · PORTLAND</div>'
                 '<div style="font:300 .9em/1.55 Lexend,system-ui,sans-serif;color:#e9dfe4;margin-top:.29em;">My moms\' bar, down a flight of stairs. Jazz on old speakers until the band plugs in, then Black Sugar takes the stage. '
                 'My kitchen stays warm long after last call. Regulars get a stool, sweetheart. Favourites get a plate.</div></div></div>').div
    g_head = frag(f'<div style="text-align:center;margin:1.29em 0 .86em;"><div style="font-family:\'Berkshire Swash\',Georgia,serif;font-size:1.5em;line-height:1.08;color:{CREAM};transform:rotate(2deg);text-shadow:{OUTLINE},.11em .11em 0 {ROSE};">My Girls</div></div>').div
    g_title.decompose()
    f2 = fold_board('#6b3a8a', 'The Underground', 'THE BAR · THE BAND', ROSE, 2, [place, g_head, g_card.extract(), g_tag.extract()])
    girls.replace_with(f2)

    # ------------------------------------------------------------ fold 3: The Regular ({user})
    chips = ''.join(f'<span style="display:inline-block;margin:.21em;padding:.36em .71em .29em;border-radius:.57em;background:#000;box-shadow:inset 0 0 0 1.5px #cfc8d288;font:700 .66em/1.2 Jura,sans-serif;letter-spacing:.12em;color:#cfc8d2;">{t}</span>'
                    for t in ('A REGULAR', "IN THE BAND'S ORBIT", 'ANY GENDER', 'ANY POV'))
    reg = frag('<div style="padding:1em 1em;border-radius:1.29em;background:linear-gradient(100deg,#0d0b0e 55%,#3a343c 92%,#6e6870);box-shadow:0 0 0 2px #000,0 .71em 1.71em #000b;">'
               f'<div style="font:700 .66em/1.3 Jura,sans-serif;letter-spacing:.2em;color:{ROSE};text-align:center;">THE STOOL I KEEP FREE</div>'
               '<p style="margin:.5em 0 0;font:300 .93em/1.65 Lexend,system-ui,sans-serif;color:#f4ebe2;text-align:center;">Somebody special has a stool at my bar and a place in the band\'s orbit. '
               'I show love with a drink set down by the right hand, a plate saved after rehearsal, and a check-in once the crowd leaves. I invite. I never force.</p>'
               f'<p style="margin:.6em 0 0;font:italic 400 1.12em/1.45 \'Crimson Text\',Georgia,serif;color:#f4ebe2;text-align:center;">So, sweetheart. Same seat tonight?</p>'
               f'<div style="text-align:center;margin-top:.71em;line-height:1;">{chips}</div></div>').div
    f3 = fold_board('#7a2346', 'You, the Regular', 'TAP TO TAKE A SEAT', CREAM, -1.5, [reg])
    f2.insert_after(f3)

    # ------------------------------------------------------------ sandbox with her chibi
    sb = kids(sandbox)[0]
    sb.clear()
    sb['style'] = sb['style'].replace('text-align:center;', '') + 'display:flex;align-items:center;justify-content:center;gap:1em;'
    sb.append(frag('<div style="line-height:0;container-type:inline-size;flex:0 0 4.6em;width:4.6em;"><img alt="Mylene chibi waving · LuvBytes" src="img/chibi.webp" style="display:block;width:100cqw;height:auto;"></div>'
                   '<div style="min-width:0;text-align:left;"><div style="font:700 1.5em/1 \'Dancing Script\',cursive;color:#cfc8d2;text-shadow:2px 2px 0 #000;">Sandbox</div>'
                   '<div style="font:300 .92em/1.5 Lexend,system-ui,sans-serif;color:#e9dfe4;margin-top:.43em;">Opener 10 is one blank page. Set the scene, sweetheart. I\'ll pour the first drink.</div></div>'))

    # ------------------------------------------------------------ songs: two showing, the rest scroll
    rows = [a.find_parent('div').find_parent('div') for a in songs.find_all('audio')]
    box = frag('<div style="flex:1 1 0;min-height:11.2em;overflow-y:auto;display:flex;flex-direction:column;gap:.36em;padding-right:.29em;scrollbar-width:thin;scrollbar-color:#ffb35c #0d0b0e;"></div>').div
    rows[0].insert_before(box)
    for r in rows:
        r['style'] += 'flex:0 0 auto;'
        box.append(r.extract())
    box.insert_after(frag('<div style="text-align:center;font:700 .6em/1.3 Jura,sans-serif;letter-spacing:.18em;color:#b3a5ae;">EIGHT SONGS · SCROLL THE LIST</div>'))

    # ------------------------------------------------------------ author's note holds the creators
    grid = creators.find('div', style=re.compile('grid-template-columns:repeat\\(3'))
    grid.extract()
    CREATORS = [('Élidan', 'a43eea09-2cc3-4d6c-8470-6d8b91b61cf3_profile-of-elidan-drakion', 'elidan'), ('Zach108', '1c335f29-911d-463b-9096-7309393209ab_profile-of-zach-108', 'zach108'),
                ('Symen', 'bf9133ed-be33-4286-b166-300ac9051c0f_profile-of-symen', 'symen'), ('Kandihara', 'd81c2c8d-384e-4392-a6cb-3b6627a9aa4e_profile-of-kandihara', 'kandihara'),
                ('Eiben', '98068345-2edf-451c-96b4-e22c218593ff_profile-of-eiben', 'eiben'), ('TuxyBoi', '4333bbf5-a12a-4501-9e94-db5cf91e70c8_profile-of-tuxyboi', 'tuxyboi'),
                ('Soheisu', '844cf7ec-fa80-46cf-a797-c1664af118aa_profile-of-soheisu', 'soheisu'), ('Seraphimus', '4e2b4813-97ef-49d4-afb7-0dbe2b2d87a5_profile-of-seraphimus', 'seraphimus'),
                ('Damascus616', 'e6491c73-b849-4288-a97f-9983803b455c_profile-of-damascus616', 'damascus616')]
    tpl = str(grid.find('a'))
    grid.clear()
    for nm, prof, slug in CREATORS:           # the same nine as Lupa's Bio, with their real avatars
        a = frag(tpl).a
        a['href'] = 'https://janitorai.com/profiles/' + prof
        im = a.find('img'); im['src'] = f'img/cr-{slug}.webp'; im['alt'] = nm + ' · LuvBytes'
        set_text(a.find_all('div')[-1], nm)
        grid.append(a)
    grid['style'] = 'display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:.71em;margin-top:.57em;font-size:.68em;max-width:26em;margin-left:auto;margin-right:auto;'
    nbody = kids(note.find('details'))[1]
    nbody.append(frag('<div style="margin-top:1em;padding-top:.86em;border-top:1px solid #ffffff1c;"><div style="text-align:center;font:700 .66em/1.3 Jura,sans-serif;letter-spacing:.2em;color:#ffb35c;">CREATORS TO FOLLOW</div></div>'))
    kids(nbody)[-1].append(grid)
    creators.decompose()

    # ------------------------------------------------------------ the E1 ending replaces the old banners and the follow card
    theme = dict(frame_bg='repeating-linear-gradient(90deg,#0000 0 34px,#7a234638 34px 50px,#0000 50px 62px,#ffffff10 62px 64px,#0000 64px 84px),'
                          'repeating-linear-gradient(0deg,#0000 0 34px,#7a234638 34px 50px,#0000 50px 62px,#ffffff10 62px 64px,#0000 64px 84px),#231c22',
                 frame_border='2px solid #cfc8d2', frame_glow='0 0 0 3px #000,0 14px 30px #000c', frame_radius='20px',
                 title_font="'Jura',Lexend,Arial,sans-serif", title_col=CREAM, title_shadow='#7a2346', ornament='🌹 ─── 🌹')
    end = frag('<div style="margin-top:2em;">' + ending_html(theme, base=base) + '</div>').div
    banners.replace_with(end)
    follow.decompose()

    # ------------------------------------------------------------ base flow: openers (with the boss fight and sandbox) before music + gallery
    for n in (a_media, songs):
        n.extract()
    sandbox.insert_after(a_media)
    a_media.insert_after(songs)

    # ------------------------------------------------------------ Kira's colour moves away from Mylene's amber; every name gets its colour
    html = str(soup)
    b0 = html.index(boss_html)
    head, tail = html[:b0], html[b0 + len(boss_html):]
    assert boss_html in html

    def colour(part):
        part = part.replace('#ff8a3d', NAMES['Kira'])
        sp = BeautifulSoup(part, 'html.parser')
        for t in list(sp.find_all(string=re.compile('|'.join(NAMES)))):
            p = t.parent
            st = p.get('style', '')
            if p.name in ('b', 'summary', 'title') or p.find_parent('summary') or p.find_parent('label') or 'color:#140a10' in st or 'Berkshire' in st or 'color:transparent' in st or 'Dancing Script' in st:
                continue
            new = re.sub('(' + '|'.join(NAMES) + ')', lambda m: f'<b style="color:{NAMES[m.group(1)]};font-weight:600;">{m.group(1)}</b>', str(t))
            t.replace_with(frag(new))
        return str(sp)

    return colour(head) + boss_html + colour(tail)


if __name__ == '__main__':
    from bio_viewer import page
    body = build('img/')
    (HERE / 'bio.html').write_text(body, encoding='utf-8')
    (HERE / 'bio-janitor.html').write_text(build(HOSTED), encoding='utf-8')
    changes = [
        'Ending: the old Ko-fi and Astral Garden banners and the follow card are gone. The last two cards are the locked Milky ending (BEFORE YOU GO ♡), capped at 640 wide on PC, with clear room around Milky so her feet and sticker outline are never cut.',
        'Order follows the base flow: openers, Red Bloom and the sandbox now come before Music & Gallery.',
        'Three folds under the jump buttons: Mylene Hart (about her), The Underground (the bar plus her girls) and You, the Regular (the player, named plainly). The openers are now about three phone screens down.',
        'Text is in her voice, first person, and no longer says "you" to the reader. Quotes, facts and the author\'s note are unchanged.',
        'Every name has its own colour with a small key in the jump box. Kira moved to a redder orange so she is not confused with Mylene.',
        'Jump buttons: Skip to the openings, Music & Gallery, Jump to the end, plus the "Click any image to enlarge it" line.',
        'Songs: two show, the rest scroll. Creators sit inside the author\'s note. Height is 5′9″ · 175 cm. Her chibi moved to the sandbox card.',
        'Red Bloom (your note of 22 Nov): the portrait card with the HP bar and the five lines stays, then it goes straight to the ending picture and SIGNAL RESTORED. The scar, the three tests and the four moves are removed.',
        'Round 2 (22 Nov evening): new hook line baked as lettering under the card picture; every opener card has a MORE arrow with the header, setup, who is there and things to do; all nine creators with their avatars.',
        'Mylene Hart has her ChatGPT name plate, and The Underground has its own bar picture.',
    ]
    html = page('Mylene / rules update', body, key='mylene-rules', accent=AMBER, changes=changes, caption='Mylene · rules update 2026-11-22 · local draft, nothing on Janitor')
    html = html.replace('<link rel="stylesheet"', '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Berkshire+Swash&family=Dancing+Script:wght@700&family=Jura:wght@700&family=Press+Start+2P&family=Lexend:wght@300;400;600;700;800&display=swap">\n<link rel="stylesheet"', 1)
    (HERE / 'index.html').write_text(html, encoding='utf-8')
    words = len(re.sub(r'<[^>]+>', ' ', body[:body.index('BOSS FIGHT')]).split())
    print('ok', len(body), 'words before boss', words)
