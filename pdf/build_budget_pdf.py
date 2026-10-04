import math, json
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether

BIRDS=500; MORT=0.05; CHICK=2900; TRANSPORT=20000; WATER=0
ST_KG=1.0; ST_BAG=25; ST_BAGCOST=80000
CONC=4700; CONC_BAG=25; MAIZE_BAG=100
MIX={"Grower mash":(120,50,900),"Finisher mash":(150,50,900)}   # maize kg, conc kg, maize UGX/kg
OPTS=[dict(key="A",name="Option A: full cycle (preferred)",sl=500,days=42,weight=2.5,price=20000,grower=1.5,fin=1.0,gr_rng="Day 15–28",fin_rng="Day 29–42"),
      dict(key="B",sl=0,name="Option B: early sale",days=29,weight=1.6,price=13000,grower=1.2,fin=0,gr_rng="Day 15–29",fin_rng="")]
VACC=[("Gumboro vaccine (500-dose vial)",500,20000),("Lasota vaccine, booster (500-dose vial)",500,20000),("NCD + IB vaccine (500-dose vial)",500,20000)]
CONS=[("Vitamins & electrolytes",2,"pack",40000,True),("Broad-spectrum antibiotic",1,"pack",80000,True),
      ("Charcoal for brooding (already purchased)",4,"bag",45000,False),("White lime (already purchased)",2.86,"bag",35000,False)]
STAFF=[("Team members (core farm staff)",2,250000)]
SUP=[("Tarpaulins *",2,"pc",60000),("Plywood sheets *",3,"pc",45000),("Basin / bucket *",1,"pc",10000),("Bar soap *",2,"bar",5000),("Sprayer",1,"pc",60000),
     ("Hard brooms",2,"pc",2000),("Squeezer / brush *",1,"pc",15000),("Small towels for wiping",2,"pc",2000),("Liquid soap, 5 litres *",1,"jerrycan",20000),
     ("Gumboots",2,"pair",10000),("Overcoats *",2,"pc",25000),("Face masks *",1,"box",10000),("Insecticide for termites *",1,"pack",25000),("Gloves",1,"box",5000)]
sup_tot=sum(q*c for _,q,_u,c in SUP)
MANURE42=1500000*BIRDS/3500

surv=round(BIRDS*(1-MORT))
st_kg=BIRDS*ST_KG; st_bags=math.ceil(st_kg/ST_BAG); st_cost=st_bags*ST_BAGCOST
health=[]
for n,vs,c in VACC:
    q=math.ceil(BIRDS/vs); health.append((n,q,"vial",c,q*c))
for n,rate,u_,c,est in CONS:
    q=math.ceil(BIRDS/1000*rate); health.append((n+(" *" if est else ""),q,u_,c,q*c))
health.append(("Water (covered under labour)",1,"lot",WATER,WATER)); health_tot=sum(h[4] for h in health); LIME=sum(h[4] for h in health if "already purchased" in h[0]); health_buy=health_tot-LIME; PRE=LIME
chicks=BIRDS*CHICK; staff_month=sum(q*r for _,q,r in STAFF)

def compute(o):
    rows=[("Broiler starter (already purchased)","Day 1–14",ST_KG,st_kg,ST_BAGCOST/ST_BAG,st_cost)]
    mz=cn=mzval=0
    for nm,kgb,rng in [("Grower mash",o["grower"],o["gr_rng"]),("Finisher mash",o["fin"],o["fin_rng"])]:
        if not kgb: continue
        m,c,mp=MIX[nm]; kg=BIRDS*kgb; mk=kg*m/(m+c); ck=kg*c/(m+c)
        rows.append((nm,rng,kgb,kg,(mk*mp+ck*CONC)/kg,mk*mp+ck*CONC)); mz+=mk; cn+=ck; mzval+=mk*mp
    mb=math.ceil(mz/MAIZE_BAG); mbc=round(mzval/mz*MAIZE_BAG); cb=math.ceil(cn/CONC_BAG)
    proc=[("Broken maize (already purchased)",mz,MAIZE_BAG,mb,mbc,mb*mbc),("25% broiler concentrate",cn,CONC_BAG,cb,CONC*CONC_BAG,cb*CONC*CONC_BAG)]
    feed_buy=proc[1][5]; maize_pre=proc[0][5]; months=o["days"]/7/4.345; labour=staff_month*months
    manure=MANURE42*o["days"]/42; slaughter=surv*o["sl"]; cash=chicks+TRANSPORT+feed_buy+health_buy+sup_tot+labour+slaughter; total=cash+st_cost+PRE+maize_pre
    rev_b=surv*o["price"]; rev=rev_b+manure
    return dict(o,slaughter=slaughter,maize_pre=maize_pre,rows=rows,proc=proc,feed_buy=feed_buy,feed_kg=sum(r[3] for r in rows),months=months,labour=labour,manure=manure,cash=cash,total=total,
                rev_b=rev_b,rev=rev,profit=rev-total,margin=(rev-total)/rev,cpb=total/surv,be=(total-manure)/surv,be_kg=(total-manure)/(surv*o["weight"]),ukg=o["price"]/o["weight"])
R_=[compute(o) for o in OPTS]; A,Bo=R_
json.dump([{k:v for k,v in r.items() if k not in("rows","proc")} for r in R_],open("data.json","w"),indent=1)
for r in R_: print(r["key"],round(r["feed_buy"]),round(r["labour"]),round(r["cash"]),round(r["total"]),round(r["rev"]),round(r["profit"]),round(r["be"]),r["proc"])

DEEP=colors.HexColor("#145C2E"); SOFT=colors.HexColor("#52685A"); FAINT=colors.HexColor("#8AA093")
INK=colors.HexColor("#16241C"); SURFACE2=colors.HexColor("#E7F0EA"); BORDER=colors.HexColor("#D2E0D6")
GOOD=colors.HexColor("#4C9A3F"); GOOD_BG=colors.HexColor("#E2F0DF"); WHITE=colors.white
def style(name,**kw):
    b=dict(fontName="Helvetica",fontSize=9,leading=12,textColor=INK); b.update(kw); return ParagraphStyle(name,**b)
BODY=style("b"); SMALL=style("s",fontSize=8,leading=10.5,textColor=SOFT); R=style("r",alignment=2); RB=style("rb",alignment=2,fontName="Helvetica-Bold")
B=style("bb",fontName="Helvetica-Bold"); TH=style("th",fontName="Helvetica-Bold",fontSize=8,textColor=SOFT); THR=style("thr",fontName="Helvetica-Bold",fontSize=8,textColor=SOFT,alignment=2)
def P(t,s=BODY): return Paragraph(t,s)
def u(x): return f"{x:,.0f}"
def section_header(text,hint=None):
    out=[Spacer(1,5*mm),P(text,style("h2",fontName="Helvetica-Bold",fontSize=12,leading=15,textColor=DEEP))]
    if hint: out.append(P(hint,style("hint",fontName="Helvetica-Oblique",fontSize=8,textColor=FAINT)))
    out.append(Spacer(1,1.5*mm)); return out
def simple_table(headers,rows,col_widths,total_row=None,bold_rows=()):
    data=[[P(h,TH if i==0 else THR) for i,h in enumerate(headers)]]
    for j,r in enumerate(rows): data.append([P(str(c),(B if j in bold_rows else BODY) if i==0 else (RB if j in bold_rows else R)) for i,c in enumerate(r)])
    if total_row: data.append([P(str(c),B if i==0 else RB) for i,c in enumerate(total_row)])
    t=Table(data,colWidths=col_widths,repeatRows=1)
    st=[("LINEBELOW",(0,0),(-1,0),0.6,BORDER),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("TOPPADDING",(0,0),(-1,-1),3.5),("BOTTOMPADDING",(0,0),(-1,-1),3.5)]
    for i in range(1,len(rows)+1): st.append(("BACKGROUND",(0,i),(-1,i),WHITE if i%2 else colors.HexColor("#F6FAF7")))
    if total_row: st.append(("LINEABOVE",(0,-1),(-1,-1),0.8,DEEP))
    t.setStyle(TableStyle(st)); return t
def kpi_tile(label,value,w,big=False):
    t=Table([[P(label,style("kl",fontSize=8,textColor=SOFT))],[P(value,style("kv",fontName="Helvetica-Bold",fontSize=15 if big else 12,leading=19 if big else 15,textColor=DEEP))]],colWidths=[w])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),SURFACE2),("LEFTPADDING",(0,0),(-1,-1),8),("TOPPADDING",(0,0),(-1,0),7),("BOTTOMPADDING",(0,-1),(-1,-1),8)])); return t
W=170*mm
def row_of(tiles):
    t=Table([tiles],colWidths=[W/len(tiles)]*len(tiles)); t.setStyle(TableStyle([("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4)])); return t

S=[]
from reportlab.platypus import Image as RLImage
logo=RLImage("smartvet_logo.png",width=20*mm,height=20*mm)
hd=Table([[logo,[P("SmartVet Africa",style("t",fontName="Helvetica-Bold",fontSize=18,leading=22,textColor=DEEP)),
            P(f"Broiler production budget · Mr. Ouma Alex · {BIRDS} birds",style("st",fontSize=10,leading=13,textColor=SOFT))],
           P("INTERNAL · VETERINARY USE",style("tag",fontSize=7,textColor=FAINT,alignment=2))]],colWidths=[23*mm,105*mm,42*mm])
hd.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"MIDDLE"),("VALIGN",(2,0),(2,0),"TOP"),("LINEBELOW",(0,0),(-1,0),1,DEEP),("BOTTOMPADDING",(0,0),(-1,-1),8),("LEFTPADDING",(0,0),(-1,-1),0)]))
S.append(hd)
S.append(Spacer(1,3*mm)); S.append(P("<b>Option A is our preferred option.</b> The birds are raised to 2.5 kg over the full 42 days and slaughtered before sale. Option B is the alternative if birds are sold early at 1.6 kg.",BODY))
S+=section_header("Batch overview","Production costs plus small farm supplies. Feeders, drinkers and housing are not included.")
S.append(simple_table(["Parameter","Option A: full cycle (preferred)","Option B: early sale"],[
  ["Day-old chicks placed",u(BIRDS),u(BIRDS)],["Birds reaching market (5% mortality)",u(surv),u(surv)],
  ["Days to sale",A["days"],Bo["days"]],["Sale weight",f"{A['weight']} kg",f"{Bo['weight']} kg"],
  ["Selling price per bird","UGX "+u(A["price"]),"UGX "+u(Bo["price"])],["Price per kg live weight","UGX "+u(A["ukg"]),"UGX "+u(Bo["ukg"])],
  ["Feed per bird",f"{A['feed_kg']/BIRDS:.1f} kg",f"{Bo['feed_kg']/BIRDS:.1f} kg"]],[80*mm,45*mm,45*mm]))
S+=section_header("Feed mixing formulas","Broken maize plus 25% broiler concentrate. No maize bran.")
S.append(simple_table(["Feed","Broken maize","Concentrate","Batch","Maize UGX/kg","Conc. UGX/kg","Mix UGX/kg"],
  [[n,f"{m} kg",f"{c} kg",f"{m+c} kg",u(mp),u(CONC),u((m*mp+c*CONC)/(m+c))] for n,(m,c,mp) in MIX.items()],[32*mm,25*mm,23*mm,18*mm,24*mm,24*mm,24*mm]))
S.append(P(f"Starter: {u(st_kg)} kg ({ST_KG:.1f} kg per bird, {st_bags} bags of {ST_BAG} kg) is <b>already purchased</b>. It is shown at UGX {u(st_cost)} so the profit is true, but it is left out of the cash still needed.",SMALL))
for r in R_:
    S+=section_header(f"{r['name']} — feed",f"Sell at {r['weight']} kg on day {r['days']}.")
    S.append(simple_table(["Stage","Period","kg/bird","Total kg","UGX/kg","Cost (UGX)"],[[a,b,f"{c:.1f}",u(e),u(f),u(g)] for a,b,c,e,f,g in r["rows"]],
      [62*mm,22*mm,17*mm,20*mm,20*mm,29*mm],["Feed consumed","","",u(r["feed_kg"]),"",u(sum(x[5] for x in r["rows"]))]))
    S.append(Spacer(1,2*mm))
    S.append(simple_table(["Mixing ingredients (whole bags)","Needed kg","Bag kg","Bags","UGX/bag","Spend (UGX)"],[[a,u(b),c,e,u(f),u(g)] for a,b,c,e,f,g in r["proc"]],
      [62*mm,22*mm,17*mm,20*mm,20*mm,29*mm],["Still to buy: concentrate only","","","","",u(r["feed_buy"])]))
S.append(KeepTogether(section_header("Health and biosecurity","Same for both options. Lines marked * are estimates to confirm with the supplier.")+[
  simple_table(["Item","Qty","Unit","Unit cost","Amount (UGX)"],[[a,b,c,u(e),u(f)] for a,b,c,e,f in health],[80*mm,15*mm,20*mm,25*mm,30*mm],["Total health and biosecurity","","","",u(health_tot)]),P(f"Charcoal and white lime (UGX {u(LIME)}) are already purchased, so UGX {u(health_buy)} is still to buy.",SMALL)]))
S.append(KeepTogether(section_header("Farm supplies and small items","Same for both options. Lines marked * are estimated quantities and prices to confirm.")+[
  simple_table(["Item","Qty","Unit","Unit cost","Amount (UGX)"],[[a,b,c,u(e),u(b*e)] for a,b,c,e in SUP],[80*mm,15*mm,20*mm,25*mm,30*mm],["Total farm supplies","","","",u(sup_tot)])]))
S.append(KeepTogether(section_header("Labour","Monthly rates prorated to the days the birds are on the farm.")+[
  simple_table(["Role","Qty","Monthly cost",f"Option A ({A['months']:.2f} mo)",f"Option B ({Bo['months']:.2f} mo)"],[[a,b,u(b*c),u(b*c*A["months"]),u(b*c*Bo["months"])] for a,b,c in STAFF],
  [62*mm,13*mm,29*mm,33*mm,33*mm],["Total labour","",u(staff_month),u(A["labour"]),u(Bo["labour"])])]))
cmp=[["Day-old chicks ("+u(BIRDS)+" × UGX "+u(CHICK)+")",u(chicks),u(chicks)],["Chick transport",u(TRANSPORT),u(TRANSPORT)],
     ["25% broiler concentrate (whole bags)",u(A["feed_buy"]),u(Bo["feed_buy"])],["Health and biosecurity (still to buy)",u(health_buy),u(health_buy)],["Farm supplies and small items",u(sup_tot),u(sup_tot)],["Labour",u(A["labour"]),u(Bo["labour"])],["Slaughtering ("+u(surv)+" birds × UGX "+u(A["sl"])+")",u(A["slaughter"]),"–"],
     ["Cash still needed",u(A["cash"]),u(Bo["cash"])],["Starter feed (already purchased)",u(st_cost),u(st_cost)],["Broken maize (already purchased)",u(A["maize_pre"]),u(Bo["maize_pre"])],["Charcoal and white lime (already purchased)",u(LIME),u(LIME)]]
S.append(KeepTogether(section_header("Production cost summary")+[simple_table(["Cost line","Option A (UGX)","Option B (UGX)"],cmp,[90*mm,40*mm,40*mm],["TOTAL PRODUCTION COST",u(A["total"]),u(Bo["total"])],bold_rows=(7,))]))
S.append(KeepTogether(section_header("Sales")+[simple_table(["Revenue line","Option A (UGX)","Option B (UGX)"],[
  [f"Live birds sold ({surv} birds)",u(A["rev_b"]),u(Bo["rev_b"])],["Manure *",u(A["manure"]),u(Bo["manure"])]],[90*mm,40*mm,40*mm],["Total revenue",u(A["rev"]),u(Bo["rev"])])]))
best=max(R_,key=lambda r:r["profit"])
badge=Table([[P("  ·  ".join(f"OPTION {r['key']} "+("PROFITABLE" if r["profit"]>0 else "MAKES A LOSS") for r in R_),style("bd",fontName="Helvetica-Bold",fontSize=8,textColor=GOOD,alignment=1))]],colWidths=[95*mm])
badge.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),GOOD_BG),("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3)])); badge.hAlign="LEFT"
S.append(KeepTogether(section_header("Result")+[badge,Spacer(1,2*mm),
  P(f"<b>Option A is our preferred option.</b> It earns UGX {u(A['profit']-Bo['profit'])} more than Option B from the same {BIRDS} chicks, after slaughtering costs.",BODY),Spacer(1,2*mm),
  row_of([kpi_tile(f"Option A (preferred) net profit ({A['days']} days, {A['weight']} kg)","UGX "+u(A["profit"]),W/2-4,big=True),kpi_tile(f"Option B net profit ({Bo['days']} days, {Bo['weight']} kg)","UGX "+u(Bo["profit"]),W/2-4,big=True)]),
  simple_table(["Measure","Option A","Option B"],[
   ["Total production cost","UGX "+u(A["total"]),"UGX "+u(Bo["total"])],["Total revenue","UGX "+u(A["rev"]),"UGX "+u(Bo["rev"])],
   ["Profit margin",f"{A['margin']:.0%}",f"{Bo['margin']:.0%}"],["Cost per bird sold","UGX "+u(A["cpb"]),"UGX "+u(Bo["cpb"])],
   ["Breakeven price per bird","UGX "+u(A["be"]),"UGX "+u(Bo["be"])],["Breakeven price per kg","UGX "+u(A["be_kg"]),"UGX "+u(Bo["be_kg"])],
   ["Profit per day on farm","UGX "+u(A["profit"]/A["days"]),"UGX "+u(Bo["profit"]/Bo["days"])]],[80*mm,45*mm,45*mm])]))
notes=["Feeders, drinkers, housing and litter are excluded. The only supplies included are the tarpaulins, plywood and small hygiene and protective items listed.",
 "Broken maize is already purchased. It is valued at UGX 900 per kg for the bags each option needs and left out of the cash still needed, so the main purchases are concentrate and veterinary supplies.",
 f"Starter feed is already purchased. It is assumed at {ST_KG:.1f} kg per bird and valued at UGX {u(ST_BAGCOST)} per {ST_BAG} kg bag. Replace this with the actual quantity and price paid.",
 "Grower is mixed at 120 kg broken maize to 50 kg concentrate, finisher at 150 kg maize to 50 kg concentrate. No maize bran is used.",
 "Option A feed is 1.5 kg grower and 1.0 kg finisher per bird. Option B is 1.2 kg grower and no finisher, with birds sold on day 29. Reaching 1.6 kg on 2.2 kg of feed needs good feed conversion.",
 "Grower and finisher are budgeted at whole-bag purchase cost: maize in 100 kg bags, concentrate in 25 kg bags. Maize is UGX 900 per kg. Concentrate at UGX 4,700 per kg is the last quote on file.",
 "Vaccines are 500-dose vials at UGX 20,000 each. Charcoal (2 bags) and lime prices come from the April 2026 costing on file. Charcoal and white lime are already purchased and are left out of the cash still needed.",
 "No anticoccidial is budgeted. Estimates (*): vitamins, antibiotic, manure value, and the quantities and prices of the farm supplies (sprayer and gumboot prices are from files). Water is not costed because the team fetches it. Chick transport is UGX 20,000. Manure is scaled from UGX 1,500,000 at 3,500 birds and reduced for the shorter Option B cycle.",
 f"Option A includes slaughtering at UGX {u(A['sl'])} per bird for the {surv} birds sold. Option B has no slaughtering cost.",
 "Labour is two team members at UGX 250,000 a month, who also mix the feed and fetch water. No casual labourers are costed.",
 f"All {u(surv)} surviving birds are assumed sold at the flat price in each option. Breakeven prices are after manure income.",
 "The custom mixes, the already-purchased starter and the two-option comparison are specific to this document and are not in the web Budget Calculator."]
S.append(KeepTogether(section_header("Assumptions and notes")+[P("•&nbsp; "+n,style("n",fontSize=8.5,leading=12,leftIndent=8,firstLineIndent=-8,spaceAfter=2)) for n in notes]))
def footer(c,doc):
    c.setFont("Helvetica",7); c.setFillColor(FAINT)
    c.drawString(20*mm,9*mm,"SmartVet Africa — Budget Calculator · prepared 4 October 2026 · for internal veterinary use. Figures are planning estimates.")
    c.drawRightString(190*mm,9*mm,f"Page {doc.page}")
SimpleDocTemplate("SmartVet Africa - Ouma Alex 500 Broiler Batch Budget.pdf",pagesize=A4,topMargin=16*mm,bottomMargin=16*mm,leftMargin=20*mm,rightMargin=20*mm,
  title="Ouma Alex 500 Broiler Batch Budget",author="SmartVet Africa").build(S,onFirstPage=footer,onLaterPages=footer)
