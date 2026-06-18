from PIL import Image, ImageDraw, ImageFont
W,H=900,675; SS=2
def F(p,s): return ImageFont.truetype(p,s*SS)
SANS="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
MONO="/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
# light windows-style palette
DESK=(180,192,205); WIN=(238,242,246); WINH=(208,222,236); TITLE=(60,90,140)
HEAD=(214,224,236); SEL=(62,166,255); LINE=(176,190,204); TXT=(40,52,66)
MUT=(110,128,146); GREEN=(39,160,110); RED=(200,40,40); WHITE=(255,255,255)
f_title=F(BOLD,15); f_h=F(BOLD,14); f_n=F(SANS,14); f_mono=F(BOLD,16); f_sm=F(SANS,12); f_btn=F(SANS,13)
frames=[]; durs=[]
def add(img,ms): frames.append(img.resize((W,H),Image.LANCZOS)); durs.append(ms)
def rrect(d,b,r,fill=None,outline=None,width=1):
    d.rounded_rectangle([v*SS for v in b],radius=r*SS,fill=fill,outline=outline,width=width*SS)

def draw(maat2, cursor=False, caption=""):
    img=Image.new("RGB",(W*SS,H*SS),DESK); d=ImageDraw.Draw(img)
    # window
    wx,wy,ww,wh=120,90,660,470
    d.rectangle([wx*SS,wy*SS,(wx+ww)*SS,(wy+wh)*SS],fill=WIN,outline=(120,140,160),width=SS)
    d.rectangle([wx*SS,wy*SS,(wx+ww)*SS,(wy+30)*SS],fill=TITLE)
    d.text(((wx+12)*SS,(wy+15)*SS),"Dieptetabel (scherm 314)",font=f_title,fill=WHITE,anchor="lm")
    d.text(((wx+ww-16)*SS,(wy+15)*SS),"✕",font=f_h,fill=WHITE,anchor="mm")
    # checkbox
    cby=wy+46
    d.rectangle([(wx+16)*SS,cby*SS,(wx+28)*SS,(cby+12)*SS],fill=WHITE,outline=(120,140,160),width=SS)
    d.text(((wx+36)*SS,(cby+6)*SS),"Sicherheitsabstand deaktiveren ?",font=f_sm,fill=TXT,anchor="lm")
    # table
    tx,ty=wx+16,wy+74; tw=ww-32
    cols=[("Nr",0,40),("Maat",40,150),("Materiaal",150,250),("Voeding [%]",250,370),("Toerental [%]",370,500)]
    d.rectangle([tx*SS,ty*SS,(tx+tw)*SS,(ty+26)*SS],fill=HEAD,outline=LINE,width=SS)
    for name,x0,x1 in cols:
        d.text(((tx+x0+8)*SS,(ty+13)*SS),name,font=f_h,fill=TXT,anchor="lm")
        d.line([(tx+x1)*SS,ty*SS,(tx+x1)*SS,(ty+26)*SS],fill=LINE,width=SS)
    rows=[("1","0.820",True,"",""),("2",maat2,True,"100","100"),("3","",False,"","")]
    ry=ty+26; rh=30
    for nr,maat,mat,voe,toer in rows:
        sel=(nr=="2")
        if sel:
            d.rectangle([tx*SS,ry*SS,(tx+tw)*SS,(ry+rh)*SS],fill=(225,238,250))
        d.rectangle([tx*SS,ry*SS,(tx+tw)*SS,(ry+rh)*SS],outline=LINE,width=SS)
        d.text(((tx+8)*SS,(ry+rh//2)*SS),nr,font=f_n,fill=TXT,anchor="lm")
        # maat cell
        if sel:
            # editable field box
            fx0,fy0,fx1,fy1=tx+44,ry+5,tx+140,ry+rh-5
            d.rectangle([fx0*SS,fy0*SS,fx1*SS,fy1*SS],fill=WHITE,outline=SEL,width=2)
            tval=str(maat)
            d.text(((fx0+8)*SS,(ry+rh//2)*SS),tval,font=f_mono,fill=(20,40,90),anchor="lm")
            if cursor:
                cxp=fx0+8+d.textlength(tval,font=f_mono)/SS+2
                d.line([cxp*SS,(ry+8)*SS,cxp*SS,(ry+rh-8)*SS],fill=(20,40,90),width=2)
            # spin arrows
            d.polygon([((fx1+6)*SS,(ry+9)*SS),((fx1+14)*SS,(ry+9)*SS),((fx1+10)*SS,(ry+4)*SS)],fill=MUT)
            d.polygon([((fx1+6)*SS,(ry+rh-9)*SS),((fx1+14)*SS,(ry+rh-9)*SS),((fx1+10)*SS,(ry+rh-4)*SS)],fill=MUT)
        else:
            d.text(((tx+48)*SS,(ry+rh//2)*SS),str(maat),font=f_n,fill=TXT,anchor="lm")
        # materiaal checkbox
        if mat:
            d.rectangle([(tx+158)*SS,(ry+9)*SS,(tx+170)*SS,(ry+21)*SS],fill=WHITE,outline=(120,140,160),width=SS)
            d.line([(tx+160)*SS,(ry+15)*SS,(tx+164)*SS,(ry+19)*SS],fill=GREEN,width=2*SS)
            d.line([(tx+164)*SS,(ry+19)*SS,(tx+169)*SS,(ry+10)*SS],fill=GREEN,width=2*SS)
        d.text(((tx+258)*SS,(ry+rh//2)*SS),voe,font=f_n,fill=TXT,anchor="lm")
        d.text(((tx+378)*SS,(ry+rh//2)*SS),toer,font=f_n,fill=TXT,anchor="lm")
        for name,x0,x1 in cols:
            d.line([(tx+x1)*SS,ry*SS,(tx+x1)*SS,(ry+rh)*SS],fill=LINE,width=SS)
        ry+=rh
    # buttons
    by=wy+wh-44
    for label,bx,prim in [("OK",wx+ww-220,True),("Annuleren",wx+ww-130,False)]:
        rrect(d,[bx,by,bx+96,by+28],4,fill=(SEL if prim else (224,230,238)),outline=(120,140,160),width=1)
        d.text(((bx+48)*SS,(by+14)*SS),label,font=f_btn,fill=(WHITE if prim else TXT),anchor="mm")
    # caption bar
    if caption:
        d.rectangle([0,(H-46)*SS,W*SS,H*SS],fill=(20,28,40))
        d.text((W//2*SS,(H-23)*SS),caption,font=f_h,fill=(180,210,240),anchor="mm")
    return img

# sequence: highlight row2 (old value), then type new value, then OK
add(draw("8.560",caption="Maat van Nr 2 selecteren (huidige maat)"),700)
# clear + type 1, 4
seqs=[("",True),("1",True),("1",False),("14",True),("14",False),("14",True)]
for val,cur in seqs:
    add(draw(val,cursor=cur,caption="Nieuwe maat invoeren…"),260)
# confirm
add(draw("14",caption="Bevestigen met OK — diepte aangepast"),900)
add(draw("14",caption="Bevestigen met OK — diepte aangepast"),700)

frames[0].save("dieptetabel.gif",save_all=True,append_images=frames[1:],duration=durs,loop=0,optimize=True,disposal=2)
import os; print("frames",len(frames),"KB",os.path.getsize("dieptetabel.gif")//1024)
