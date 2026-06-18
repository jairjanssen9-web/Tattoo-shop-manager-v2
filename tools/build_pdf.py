from PIL import Image, ImageDraw, ImageFont, ImageOps

W,H = 1240,1754      # A4 @ ~150dpi
M = 90               # margin
CW = W-2*M           # content width
SANS="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def F(p,s): return ImageFont.truetype(p,s)

# light print theme
BG=(255,255,255); TXT=(27,37,48); MUT=(92,113,134); ACC=(47,127,209)
ACC_BG=(232,242,252); LINE=(214,224,234); ELU=(226,0,26); GREEN=(33,160,110)
WARN_BG=(255,243,240); WARN_LINE=(240,180,170); AMBER=(200,140,20)

f_h1=F(BOLD,62); f_model=F(BOLD,30); f_h2=F(BOLD,40); f_step_t=F(BOLD,27)
f_body=F(SANS,25); f_bodyb=F(BOLD,25); f_small=F(SANS,20); f_lab=F(BOLD,20)
f_num=F(BOLD,28); f_tag=F(BOLD,18); f_cap=F(SANS,19)

pages=[]; img=None; d=None; y=0
def new_page():
    global img,d,y
    img=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(img); y=M
    pages.append(img)
def need(h):
    global y
    if y+h > H-M: new_page()
new_page()

def wrap(text,font,maxw):
    words=text.split(); lines=[]; cur=""
    for w in words:
        t=(cur+" "+w).strip()
        if d.textlength(t,font=font)<=maxw: cur=t
        else:
            if cur: lines.append(cur)
            cur=w
    if cur: lines.append(cur)
    return lines

def rich_segments(text):
    # split **bold** segments
    out=[]; i=0
    while i<len(text):
        j=text.find("**",i)
        if j<0: out.append((text[i:],False)); break
        if j>i: out.append((text[i:j],False))
        k=text.find("**",j+2)
        if k<0: out.append((text[j:],False)); break
        out.append((text[j+2:k],True)); i=k+2
    return out

def para(text,x=M,maxw=CW,fill=TXT,lh=38,font=f_body,fontb=f_bodyb,gap=8):
    # word-wrap with inline bold (**)
    global y
    segs=rich_segments(text)
    # tokenize into (word, bold)
    tokens=[]
    for s,b in segs:
        parts=s.split(" ")
        for idx,p in enumerate(parts):
            if p=="" and idx>0: continue
            tokens.append((p,b))
    line=[]; lw=0; space=d.textlength(" ",font=font)
    def flush():
        nonlocal line,lw
        need(lh); xx=x
        for w,b in line:
            fnt=fontb if b else font
            d.text((xx,y),w,font=fnt,fill=fill); xx+=d.textlength(w,font=fnt)+space
        globals()['y']+=lh; line=[]; lw=0
    for w,b in tokens:
        fnt=fontb if b else font
        ww=d.textlength(w,font=fnt)
        if lw+ww>maxw and line: flush()
        line.append((w,b)); lw+=ww+space
    if line: flush()
    globals()['y']+=gap

def heading(badge,title,sub=None,alt=False):
    global y
    need(96)
    bs=64
    d.rounded_rectangle([M,y,M+bs,y+bs],14,fill=(ELU if alt else ACC))
    d.text((M+bs/2,y+bs/2),badge,font=f_num,fill=(255,255,255),anchor="mm")
    d.text((M+bs+22,y+8),title,font=f_h2,fill=TXT)
    if sub:
        d.text((M+bs+24,y+52),sub,font=f_small,fill=MUT)
    y+=bs+26

def tldr(items):
    global y
    pad=22; lh=34
    # measure height
    lines_total=0; wrapped=[]
    for it in items:
        wl=[]
        for ln in wrap_rich(it,f_body,CW-2*pad-30): wl.append(ln)
        wrapped.append(wl); lines_total+=len(wl)
    boxh=pad*2+30+lines_total*lh+ (len(items)-1)*6
    need(boxh+16)
    d.rounded_rectangle([M,y,M+CW,y+boxh],16,fill=ACC_BG,outline=(190,216,240),width=2)
    yy=y+pad
    d.text((M+pad,yy),"⚡ IN HET KORT",font=f_lab,fill=ACC); yy+=34
    n=1
    for wl in wrapped:
        # number
        d.ellipse([M+pad,yy+3,M+pad+22,yy+25],fill=ACC)
        d.text((M+pad+11,yy+14),str(n),font=f_small,fill=(255,255,255),anchor="mm")
        for i,(segs) in enumerate(wl):
            xx=M+pad+34
            for w,b in segs:
                fnt=f_bodyb if b else f_body
                d.text((xx,yy),w,font=fnt,fill=TXT); xx+=d.textlength(w,font=fnt)+d.textlength(" ",font=f_body)
            yy+=lh
        yy+=6; n+=1
    y+=boxh+22

def wrap_rich(text,font,maxw):
    # returns list of lines, each line is list of (word,bold)
    segs=rich_segments(text); tokens=[]
    for s,b in segs:
        for p in s.split(" "):
            if p!="": tokens.append((p,b))
    lines=[]; line=[]; lw=0; space=d.textlength(" ",font=font)
    for w,b in tokens:
        ww=d.textlength(w,font=f_bodyb if b else font)
        if lw+ww>maxw and line: lines.append(line); line=[]; lw=0
        line.append((w,b)); lw+=ww+space
    if line: lines.append(line)
    return lines

def step(n,title,body):
    global y
    need(70)
    cs=46
    d.ellipse([M,y,M+cs,y+cs],outline=ACC,width=3)
    d.text((M+cs/2,y+cs/2),str(n),font=f_num,fill=ACC,anchor="mm")
    d.text((M+cs+20,y+6),title,font=f_step_t,fill=TXT)
    y+=cs+8
    para(body,x=M+cs+20,maxw=CW-cs-20,gap=16)

def image(path,maxw=CW-120,cap=None,center=True):
    global y
    im=ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    w,h=im.size
    if w>maxw:
        im=im.resize((int(maxw),int(h*maxw/w)),Image.LANCZOS)
    iw,ih=im.size
    caph=30 if cap else 0
    need(ih+caph+24)
    x=M+(CW-iw)//2 if center else M
    img.paste(im,(x,y))
    d.rectangle([x,y,x+iw,y+ih],outline=LINE,width=2)
    y+=ih+6
    if cap:
        for ln in wrap(cap,f_cap,CW):
            d.text((M+(CW-d.textlength(ln,font=f_cap))//2,y),ln,font=f_cap,fill=MUT); y+=26
    y+=20

def warn(text):
    global y
    pad=18
    lines=wrap_rich(text,f_body,CW-2*pad)
    boxh=pad*2+len(lines)*34
    need(boxh+12)
    d.rounded_rectangle([M,y,M+CW,y+boxh],14,fill=WARN_BG,outline=WARN_LINE,width=2)
    yy=y+pad
    for ln in lines:
        xx=M+pad
        for w,b in ln:
            fnt=f_bodyb if b else f_body
            d.text((xx,yy),w,font=fnt,fill=(150,40,30)); xx+=d.textlength(w,font=fnt)+d.textlength(" ",font=f_body)
        yy+=34
    y+=boxh+18

def divider():
    global y
    need(40); d.line([M,y+10,M+CW,y+10],fill=LINE,width=2); y+=40

def codes_table(rows):
    global y
    rh=46; th=46; tw=CW
    need(th+len(rows)*rh+10)
    d.rectangle([M,y,M+tw,y+th],fill=ACC_BG)
    d.text((M+16,y+th/2),"Bestelnummer",font=f_lab,fill=TXT,anchor="lm")
    d.text((M+tw*0.5,y+th/2),"Specificatie",font=f_lab,fill=TXT,anchor="lm")
    y+=th
    for code,spec in rows:
        d.rectangle([M,y,M+tw,y+rh],outline=LINE,width=1)
        d.text((M+16,y+rh/2),code,font=f_bodyb,fill=ACC,anchor="lm")
        d.text((M+tw*0.5,y+rh/2),spec,font=f_body,fill=TXT,anchor="lm")
        y+=rh
    y+=22

# ================= COVER =================
y=300
d.text((W/2,y),"elu",font=f_h1,fill=ELU,anchor="rm"); d.text((W/2,y),"matec",font=f_h1,fill=TXT,anchor="lm")
y+=70
d.text((W/2,y),"Werkinstructie  ·  SBZ 122/71",font=f_model,fill=TXT,anchor="mm"); y+=70
d.text((W/2,y),"Profielbewerkingscentrum — CNC beneden",font=f_small,fill=MUT,anchor="mm"); y+=90
# intro box
para("Een naslagwerk om de machine zelfstandig en op eigen tempo te leren bedienen. "
     "Weet je iets even niet meer? Blader naar de juiste taak — alle stappen staan er met foto's bij.",
     x=M+60,maxw=CW-120,fill=TXT)
y+=20
d.line([M+60,y,M+CW-60,y],fill=LINE,width=2); y+=40
d.text((M+60,y),"INHOUD",font=f_lab,fill=ACC); y+=44
for t in ["De machine — specificaties","Het besturingssysteem (eluCad / eci2)",
          "Taak 1 · Machine opstarten","Taak 2 · Spindel / frees vervangen","Taak 3 · Diepteverschil maken"]:
    d.text((M+60,y),"•  "+t,font=f_body,fill=TXT); y+=40

# ================= MACHINE =================
new_page()
heading("i","De machine",sub="Elumatec SBZ 122/71",alt=True)
para("De SBZ 122/71 is een CNC-profielbewerkingscentrum voor **aluminium, PVC en dunwandige stalen profielen**. "
     "Aansturing via de **eci2**-interface en de **eluCad**-software — programmeren via een grafische interface, zonder ISO-code.")
specs=[("Toerental freesspindel","24.000 min⁻¹ · 8 kW · luchtgekoeld"),
       ("Gereedschapsopname","HSK-F63 · automatische wisseling"),
       ("Positioneernauwkeurigheid","± 0,1 mm"),
       ("Bewerkingsrichtingen","5 (boven, achter, voor, links, rechts)"),
       ("Magazijnplaatsen","4 (max. 16)"),
       ("Slag X / Y / Z","4.295 / 910 / 475 mm"),
       ("Max. bewerkingslengte","4.150 mm"),
       ("Afmetingen (L×D×H)","6.592 × 2.171 × 3.000 mm · ± 2.900 kg")]
rh=44
for k,v in specs:
    need(rh)
    d.text((M,y),k,font=f_bodyb,fill=MUT)
    d.text((M+CW,y),v,font=f_body,fill=TXT,anchor="ra")
    y+=rh
y+=10
para("De eluCad-desktop zoals die er na het opstarten uitziet (F3 = Tool Management):",fill=MUT,font=f_small)
image("/tmp/pdf_os.png",maxw=CW-80,cap="eluCad-besturing — menubalk, programmalijst, 3D-weergave en de F-toetsen onderaan.")

# ================= TAAK 1 =================
new_page()
heading("1","Machine opstarten",sub="Van stroom aan tot bedrijfsklaar")
tldr(["**Stroom aan** met de grote schakelaar aan de zijkant.",
      "Scherm gaat aan en **logt automatisch in**.",
      "Druk de **stuurspanning** aan — blauwe knop links onderin.",
      "Wacht tot de **4 controles** klaar zijn → bedrijfsklaar."])
step(1,"Zet de stroom aan","Schakel de stroom in met de **grote schakelaar aan de zijkant** van de machine.")
step(2,"Wacht tot het scherm aangaat","Het scherm start op en **logt automatisch in**. Je komt in de eluCad-besturing.")
step(3,"Druk de stuurspanning aan","Druk op de **blauwe knop links onderin** het bedieningspaneel.")
image("images/bedieningspaneel.png",maxw=CW-160,cap="Bedieningspaneel — stuurspanning links onderin, naast de noodstop (rood) en de sleutelschakelaar.")
step(4,"Machinestatus verschijnt","De besturing controleert vanzelf vier basispunten: positie/referentie, detectiebundel, opwarming en onderhoudsinformatie.")
image("/tmp/pdf_status.png",maxw=CW-80,cap="Machinestatus — de vier controles worden één voor één afgevinkt.")
step(5,"Bedrijfsklaar","Zodra alle controles klaar zijn, is de machine gereed. Wacht hier altijd op.")

# ================= TAAK 2 =================
new_page()
heading("2","Spindel / frees vervangen",sub="Gereedschap inlezen, opmeten en plaatsen")
tldr(["Ga naar **F3 · Tool Management** en kies het juiste **magazijn**.",
      "Kies een bestaand gereedschap, of lees een nieuw in via **Bewerkingen → Gereedschappen → Nieuw**.",
      "**Meet de lengte**; bij kleine frezen **+1 mm** voor de spantang.",
      "**F3 → Gereedschapwisselaar**: houder kiezen → opvullen → freeskop inzetten → **Start**."])
step(1,"Open Tool Management (F3)","Voor handmatig vervangen ga je naar **F3** — het gereedschapsbeheer.")
step(2,"Kies het juiste magazijn","Er zijn **vijf magazijnen** met nummers; die zie je ook in de machine zelf.")
step(3,"Bestaand gereedschap kiezen","Er staat een rij **al ingewerkte frezen** met vaste afmetingen. Daar kun je direct uit kiezen.")
image("images/gereedschapsselectie.png",maxw=CW-200,cap="Gereedschapsselectie — bestaande frezen met type, zijde, gewicht en magazijn.")
step(4,"Of: nieuw standaardgereedschap","Ga naar **Bewerkingen → Gereedschappen → Nieuw** — selectie van 124 standaardgereedschappen.")
step(5,"Gebruik de juiste bestelcodes","Koppel altijd de juiste code aan de juiste aangekochte tool.")
warn("⚠  Let op: verkeerde codes bij de verkeerde tool geven problemen. Controleer dit altijd.")
codes_table([("136 35 08 17","Dia 63 mm / lengte 67"),
             ("136 35 08 13","Standaard houder (type 13)"),
             ("136 35 08 18","Standaard houder (type 18)")])
step(6,"Bepaal het houdertype","Dubbelklik op een ingelezen gereedschap; de **laatste twee cijfers** van het houdernummer zijn het type (18 / 13 / 00 standaard).")
step(7,"Meet de geometrie (lengte)","Meet de totale lengte met een **accurate metalen maatstaf** en zet de frees vast in de houder. De geometrie kun je later nog aanpassen.")
step(8,"Reken +1 mm voor de spantang","Is de spantang nog niet vast? Reken **1 mm méér** — bij kleine frezen trekt de spantang de frees nog ±1 mm dieper bij het aandraaien.")
step(9,"Laat de machine de frees plaatsen","F3 → **Gereedschapwisselaar tonen** → gereedschap opnemen → opvullen → kies de spindelhouder (bv. 123) → gereedschap plaats opvullen → freeskop inzetten → **Start**. De machine plaatst hem zelf op de gekozen magazijnplek.")

# ================= TAAK 3 =================
new_page()
heading("3","Diepteverschil maken",sub="Een macro aanpassen via de Dieptetabel (scherm 314)")
tldr(["Open het **programma** → je komt in het teken- en bewerkingssysteem.",
      "Klik op **Profiel** → kies de **zijde** → klik de **macro** aan (cirkel of rechthoek).",
      "Klik rechtsonder op **Dieptetabel**.",
      "Pas de **Maat** (diepte) aan bij Nr 2 en bevestig met **OK**."])
step(1,"Open het programma","Klik op het programma en open de programmagegevens — je komt in het **teken- en bewerkingssysteem**.")
step(2,"Kies het profiel","Klik bovenin op **Profiel**.")
step(3,"Kies de zijde (facing)","Klik aan welke **zijde** je wilt veranderen, bijvoorbeeld 'boven'.")
image("images/macro_list.jpg",maxw=CW-260,cap="Macrolijst — elke regel is een macro (hier Cirkel) op de zijde 'boven', met X / Y / Z.")
step(4,"Selecteer de macro","Klik de **macro** aan die je wilt aanpassen — een **cirkel** of een **rechthoek**.")
step(5,"Open de Dieptetabel","Zodra de macro geselecteerd is, verschijnt **rechtsonder** de knop **Dieptetabel**. Klik die aan.")
step(6,"Verander de maat (diepte)","In de **Dieptetabel (scherm 314)** pas je de **Maat** aan — dat is de diepte. Nu staat hij op maat twee (Nr 2). Vul de nieuwe waarde in en bevestig met **OK**.")
image("images/dieptetabel.jpg",maxw=CW-260,cap="Dieptetabel (scherm 314) op de machine — de maat van Nr 2 wordt aangepast (hier naar 14).")

# ================= TAAK 4 =================
new_page()
heading("4","Een profiel invoeren",sub="Profielselectie · Programmaheader (scherm 312)")
tldr(["Geen profiel? Klik op **Verder** → de **Profielselectie** opent.",
      "**Selecteer het profiel** (met voorvertoning) en bevestig met OK.",
      "Controleer in de **Programmaheader (scherm 312)** of alles klopt.",
      "Klik op **Verder** → de bewerkingen worden op het profiel gezet."])
step(1,"Open de profielselectie","Is er bij een bewerking **geen profiel** meer ingesteld, klik dan op **Verder**. Er opent automatisch een **Profielselectie** (menu 24).")
step(2,"Kies het juiste profiel","Klik het profiel aan in de lijst. Rechts zie je een **voorvertoning** van de doorsnede met afmetingen. Bevestig met **OK**.")
image("images/profielselectie.jpg",maxw=CW-220,cap="Profielselectie (menu 24) — profielen uit de eluCad-catalogus met voorvertoning (hier 48 x 100).")
para("De profielen staan in **eluCad** als standaard profielencatalogus: daar kun je tekenen en aanpassen. Het kan ook in het **Machine Control Center (eluCam)**, maar minder gemakkelijk dan in eluCad.",fill=MUT,font=f_small,lh=30)
step(3,"Controleer de instellingen","In de **Programmaheader (scherm 312)** controleer je de variaties: lengte, opspanorientatie/spiegeling, de zaaghoeken (boven en voor) en de zijde.")
image("images/programmaheader.jpg",maxw=CW-220,cap="Programmaheader (scherm 312) - naam, lengte, orientatie/spiegeling en zaaghoeken.")
step(4,"Verder: bewerkingen op het profiel","Staan alle variaties goed? Klik op **Verder**. Het profiel wordt geladen (je ziet de doorsnede) en de machine zet de **bewerkingen op het profiel**.")
image("images/profiel_geladen.jpg",maxw=CW-220,cap="Het geselecteerde profiel is geladen en wordt weergegeven - klaar voor de bewerkingen.")
para("Voorbeeld: 'Hang stomp afgerond' is een **Obi 100**-profiel (eigen product) met een afronding. Wordt weinig meer gebruikt, maar er zijn bewerkingen van - bijvoorbeeld een glazen kaderdeur of een houten hangdeur.",fill=MUT,font=f_small,lh=30)

# footer page numbers
for i,p in enumerate(pages):
    dd=ImageDraw.Draw(p)
    dd.text((W/2,H-50),"Elumatec SBZ 122/71 · Werkinstructie    —    %d / %d"%(i+1,len(pages)),
            font=f_cap,fill=(160,172,186),anchor="mm")

pages[0].save("Werkinstructie-SBZ122-71.pdf",save_all=True,append_images=pages[1:],resolution=150.0)
import os
print("pages:",len(pages),"PDF MB: %.2f"%(os.path.getsize("Werkinstructie-SBZ122-71.pdf")/1024/1024))
