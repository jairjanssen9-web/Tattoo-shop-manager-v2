from PIL import Image, ImageDraw, ImageFont

W,H = 900,675
SS = 2  # supersample for crisp text
def F(path,size): return ImageFont.truetype(path,size*SS)
SANS   = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD   = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
MONO   = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

# palette
BG=(10,14,21); CARD=(28,38,50); CARD2=(34,46,60); LINE=(44,58,75)
TXT=(232,238,245); MUTED=(148,166,186); ACC=(62,166,255); ACC2=(47,127,209)
GREEN=(39,192,138); AMBER=(255,176,46); ELU=(226,0,26); WHITE=(255,255,255)

def new(bg=BG):
    img=Image.new("RGB",(W*SS,H*SS),bg)
    return img, ImageDraw.Draw(img)

def ctext(d,cx,y,txt,font,fill,anchor="mm"):
    d.text((cx*SS,y*SS),txt,font=font,fill=fill,anchor=anchor)

def rrect(d,box,r,fill=None,outline=None,width=1):
    box=[v*SS for v in box]
    d.rounded_rectangle(box,radius=r*SS,fill=fill,outline=outline,width=width*SS)

def finish(img):
    return img.resize((W,H),Image.LANCZOS)

frames=[]; durations=[]
def add(img,ms): frames.append(finish(img)); durations.append(ms)

# ---------- fonts ----------
f_logo=F(BOLD,46); f_sub=F(SANS,15); f_mono=F(MONO,13); f_h=F(BOLD,22)
f_t=F(BOLD,18); f_n=F(SANS,15); f_sm=F(SANS,12); f_b=F(BOLD,15); f_big=F(BOLD,60)
f_menu=F(SANS,13); f_tree=F(SANS,12); f_fk=F(BOLD,12); f_fks=F(SANS,10)

# ================= BOOT =================
bootmsgs=["systeem laden…","besturing initialiseren…","assen registreren…","eci2 starten…","gereed."]
for i in range(16):
    img,d=new((8,11,17))
    p=i/15
    ctext(d,W//2,H//2-70,"elu",f_logo,ELU,anchor="rm")
    ctext(d,W//2,H//2-70,"matec",f_logo,WHITE,anchor="lm")
    ctext(d,W//2,H//2-28,"eci2  ·  SBZ 122/71",f_sub,MUTED)
    bw,bh=460,8; bx=(W-bw)//2; by=H//2+10
    rrect(d,[bx,by,bx+bw,by+bh],4,fill=LINE)
    rrect(d,[bx,by,bx+int(bw*p),by+bh],4,fill=ELU)
    ctext(d,W//2,by+34,bootmsgs[min(int(p*4.999),4)],f_mono,MUTED)
    add(img,90)

# ================= LOGIN =================
import math
for i in range(12):
    img,d=new((14,20,32))
    cx,cy=W//2,H//2-26; R=34
    # spinner ring base
    d.ellipse([(cx-R)*SS,(cy-R)*SS,(cx+R)*SS,(cy+R)*SS],outline=LINE,width=5*SS)
    a0=(i/12)*360
    d.arc([(cx-R)*SS,(cy-R)*SS,(cx+R)*SS,(cy+R)*SS],a0,a0+90,fill=ACC,width=5*SS)
    ctext(d,W//2,cy+64,"Automatisch aanmelden…",f_t,(207,224,240))
    ctext(d,W//2,cy+92,"gebruiker: MACHINE · besturing wordt geladen",f_mono,MUTED)
    add(img,85)

# ================= OS DESKTOP =================
def draw_os(highlightF3=True):
    img=Image.new("RGB",(W*SS,H*SS),(190,200,212)); d=ImageDraw.Draw(img)
    # title bar
    d.rectangle([0,0,W*SS,34*SS],fill=(44,58,75))
    d.ellipse([(12)*SS,11*SS,(24)*SS,23*SS],fill=ELU)
    d.text((34*SS,17*SS),"eluCad — SBZ 122/71",font=f_menu,fill=WHITE,anchor="lm")
    for k,x in [("—",W-66),("▢",W-44),("✕",W-22)]:
        d.text((x*SS,17*SS),k,font=f_menu,fill=WHITE,anchor="mm")
    # menu bar
    d.rectangle([0,34*SS,W*SS,60*SS],fill=(238,243,248))
    items=["Bewerkingen","Gereedschappen","Database","Sortering","Help"]
    x=14
    for it in items:
        w=d.textlength(it,font=f_menu)/SS+18
        if it=="Bewerkingen":
            rrect(d,[x,40,x+w,55],5,fill=ACC)
            d.text(((x+9)*SS,47*SS),it,font=f_menu,fill=WHITE,anchor="lm")
        else:
            d.text(((x+9)*SS,47*SS),it,font=f_menu,fill=(44,58,75),anchor="lm")
        x+=w+4
    # body: sidebar + main
    d.rectangle([0,60*SS,W*SS,H*SS],fill=WHITE)
    d.rectangle([0,60*SS,300*SS,H*SS],fill=(244,248,251))
    d.line([300*SS,60*SS,300*SS,H*SS],fill=(205,217,228),width=SS)
    tree=[("▾ Programma's",0,(51,72,92),True),("C-SchSmaLL3",1,(92,113,134),False),
          ("C-SchSmaLL4",1,(92,113,134),False),("C-SchSmaRe5",1,(92,113,134),False),
          ("▸ 3D-Scharnier",0,(51,72,92),True),("▸ eluCad imports",0,(51,72,92),True),
          ("▸ Glasdeur",0,(51,72,92),True),("▸ Hang, Slamp en Update",0,(51,72,92),True)]
    ty=78
    for label,lvl,col,bold in tree:
        d.text(((16+lvl*16)*SS,ty*SS),label,font=f_tree,fill=col,anchor="lm")
        ty+=24
    # main table
    mx,my=320,76
    headers=["Pos","Programma","Nulpunt","St."]; colx=[mx,mx+44,mx+250,mx+330]
    d.rectangle([mx*SS,(my-4)*SS,(W-16)*SS,(my+18)*SS],fill=(223,233,241))
    for hx,h in zip(colx,headers):
        d.text((hx*SS+6*SS,(my+7)*SS),h,font=f_tree,fill=(51,72,92),anchor="lm")
    rows=[("1","C-SchSmaLL3","1","0",True),("2","C-SchSmaLL4","1","0",False),
          ("3","C-SchSmaRe5","1","0",False),("4","deurdranger","1","0",False),
          ("5","deurdranger1","1","0",False)]
    ry=my+22
    for pos,nm,nul,st,sel in rows:
        if sel:
            d.rectangle([mx*SS,ry*SS,(W-16)*SS,(ry+22)*SS],fill=ACC)
            tc=WHITE
        else:
            tc=(44,58,75)
        for hx,val in zip(colx,[pos,nm,nul,st]):
            d.text((hx*SS+6*SS,(ry+11)*SS),val,font=f_tree,fill=tc,anchor="lm")
        ry+=22
    # 3D box
    bx0,by0,bx1,by1=W-330,H-250,W-26,H-120
    d.rectangle([bx0*SS,by0*SS,bx1*SS,by1*SS],fill=(20,28,40),outline=(51,72,92),width=SS)
    d.polygon([( (bx0+50)*SS,(by1-50)*SS),((bx1-40)*SS,(by0+70)*SS),((bx1-20)*SS,(by0+86)*SS),((bx0+70)*SS,(by1-34)*SS)],fill=ACC)
    d.text(((bx0+10)*SS,(by1-16)*SS),"3D-weergave",font=f_sm,fill=(92,113,134),anchor="lm")
    # F-keys
    fy=H-56
    d.rectangle([0,fy*SS,W*SS,H*SS],fill=(205,217,228))
    fkeys=[("F1","Help"),("F2","Open"),("F3","Tools"),("F4","Edit"),("F5","Sim"),("F6","Magazijn"),("F7","Nulpunt"),("F8","Start")]
    fw=W/8
    for idx,(k,lbl) in enumerate(fkeys):
        x0=idx*fw+4; x1=(idx+1)*fw-4
        hi=(k=="F3" and highlightF3)
        rrect(d,[x0,fy+5,x1,H-6],5,fill=(ACC2 if hi else (236,243,248)),outline=(185,200,212),width=1)
        cxk=(x0+x1)/2
        d.text((cxk*SS,(fy+22)*SS),k,font=f_fk,fill=(WHITE if hi else ACC2),anchor="mm")
        d.text((cxk*SS,(fy+40)*SS),lbl,font=f_fks,fill=(WHITE if hi else (51,72,92)),anchor="mm")
    return img

for i in range(10):
    img=draw_os(highlightF3=(i%4<2))  # blink F3
    add(img,110)

# ================= STUURSPANNING =================
for i in range(12):
    img,d=new((9,13,20))
    ctext(d,W//2,H//2-110,"Druk de stuurspanning aan",f_h,(207,224,240))
    cx,cy=W//2,H//2; R=58
    # pulse ring
    pr=R+14+int((i%6)*6)
    alpha_ring=ACC
    d.ellipse([(cx-pr)*SS,(cy-pr)*SS,(cx+pr)*SS,(cy+pr)*SS],outline=ACC,width=2*SS)
    # button
    d.ellipse([(cx-R)*SS,(cy-R)*SS,(cx+R)*SS,(cy+R)*SS],fill=(47,127,209),outline=(26,79,134),width=3*SS)
    d.ellipse([(cx-R+10)*SS,(cy-R+8)*SS,(cx-6)*SS,(cy-10)*SS],fill=(111,192,255))  # highlight
    # power symbol
    d.ellipse([(cx-20)*SS,(cy-16)*SS,(cx+20)*SS,(cy+24)*SS],outline=WHITE,width=4*SS)
    d.rectangle([(cx-2)*SS,(cy-26)*SS,(cx+2)*SS,(cy+2)*SS],fill=(47,127,209))
    d.rectangle([(cx-3)*SS,(cy-26)*SS,(cx+3)*SS,(cy-2)*SS],fill=WHITE)
    ctext(d,W//2,cy+R+44,"blauwe knop — links onderin het bedieningspaneel",f_sm,MUTED)
    add(img,95)

# ================= MACHINE STATUS =================
checks=["Positie- / referentiecontrole","Detectiebundel (lichtscherm)","Opwarming spindel","Onderhoudsinformatie"]
def draw_status(progress):  # progress: list of 4 floats 0..1, and done flags derived
    img,d=new((12,20,32))
    title="Machinestatus — basiscontrole"
    tw=d.textlength(title,font=f_h)/SS
    d.text(((W//2+12)*SS,60*SS),title,font=f_h,fill=(207,224,240),anchor="mm")
    dotx=W//2 - tw/2 - 14
    d.ellipse([(dotx-6)*SS,54*SS,(dotx+6)*SS,66*SS],fill=AMBER)
    y=120; rowh=92; pad=70
    for idx,name in enumerate(checks):
        pr=progress[idx]
        done=pr>=1.0; running=0<pr<1.0
        x0,x1=pad,W-pad
        rrect(d,[x0,y,x1,y+rowh-18],12,fill=CARD,outline=LINE,width=1)
        # icon
        icx,icy=x0+34,y+(rowh-18)//2
        ic_col=GREEN if done else (CARD2)
        ic_out=GREEN if done else (ACC if running else (51,72,92))
        d.ellipse([(icx-17)*SS,(icy-17)*SS,(icx+17)*SS,(icy+17)*SS],fill=ic_col,outline=ic_out,width=2*SS)
        d.text((icx*SS,icy*SS),("✓" if done else str(idx+1)),font=f_b,
               fill=((4,17,13) if done else (ACC if running else MUTED)),anchor="mm")
        # name
        d.text(((x0+66)*SS,icy*SS),name,font=f_n,fill=(174,191,206),anchor="lm")
        # progress bar
        bw=150; bx=x1-bw-90; by=icy-4
        rrect(d,[bx,by,bx+bw,by+8],4,fill=(28,38,50))
        if pr>0: rrect(d,[bx,by,bx+int(bw*min(pr,1)),by+8],4,fill=(GREEN if done else ACC))
        # status text
        stt = "OK" if done else ("bezig…" if running else "wacht")
        stc = GREEN if done else (ACC if running else MUTED)
        d.text(((x1-20)*SS,icy*SS),stt,font=f_sm,fill=stc,anchor="rm")
        y+=rowh
    return img

# animate: each check fills sequentially
seq=[0.0,0.0,0.0,0.0]
# initial wait
add(draw_status(seq[:]),200)
for c in range(4):
    for step in range(6):
        seq[c]=(step+1)/6
        add(draw_status(seq[:]),70)
    seq[c]=1.0
    add(draw_status(seq[:]),120)
add(draw_status([1,1,1,1]),400)

# ================= READY =================
for i in range(10):
    img,d=new((9,28,22))
    cx,cy=W//2,H//2-30; R=48
    glow=R+ (i%5)*4
    d.ellipse([(cx-glow)*SS,(cy-glow)*SS,(cx+glow)*SS,(cy+glow)*SS],outline=(20,90,66),width=2*SS)
    d.ellipse([(cx-R)*SS,(cy-R)*SS,(cx+R)*SS,(cy+R)*SS],fill=GREEN)
    d.text((cx*SS,cy*SS),"✓",font=f_big,fill=(4,20,13),anchor="mm")
    ctext(d,W//2,cy+R+40,"Bedrijfsklaar",f_h,(223,250,239))
    ctext(d,W//2,cy+R+70,"Alle controles doorlopen — machine gereed voor gebruik",f_sm,(143,220,192))
    add(img,120)
# hold on ready
add(frames[-1].copy(),900)

# ---- save GIF ----
frames[0].save("besturingssysteem.gif",save_all=True,append_images=frames[1:],
               duration=durations,loop=0,optimize=True,disposal=2)
print("frames:",len(frames))
import os; print("GIF KB:",os.path.getsize("besturingssysteem.gif")//1024)
