package com.oliven.app;

import android.app.*;
import android.os.*;
import android.content.*;
import android.graphics.*;
import android.view.*;
import android.widget.*;
import java.text.*;
import java.util.*;

public class MainActivity extends Activity {
    OlivenView view;

    @Override public void onCreate(Bundle b) {
        super.onCreate(b);
        Window w = getWindow();
        w.setStatusBarColor(Color.rgb(250,251,248));
        w.setNavigationBarColor(Color.BLACK);
        if (Build.VERSION.SDK_INT >= 30) w.setDecorFitsSystemWindows(true);
        if (Build.VERSION.SDK_INT >= 23) {
            w.getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR);
        }
        view = new OlivenView(this);
        setContentView(view);
    }

    static class Habit {
        int id; String name, goal, cat;
        Habit(int id, String name, String goal, String cat){ this.id=id; this.name=name; this.goal=goal; this.cat=cat; }
    }

    static class Hit {
        RectF r; int type, index;
        Hit(float l,float t,float rr,float b,int type,int index){ r=new RectF(l,t,rr,b); this.type=type; this.index=index; }
    }

    static class OlivenView extends View {
        final int BG=Color.rgb(250,251,248), WHITE=Color.WHITE, TEXT=Color.rgb(24,31,26), MUTED=Color.rgb(105,112,106);
        final int GREEN=Color.rgb(31,111,78), GREEN_DARK=Color.rgb(20,84,58), GREEN2=Color.rgb(59,139,91), OLIVE=Color.rgb(116,138,53);
        final int SOFT=Color.rgb(226,246,237), SOFT2=Color.rgb(240,248,242), BORDER=Color.rgb(222,228,220), LIGHT=Color.rgb(235,241,234), BLACK=Color.rgb(2,3,2);
        final Paint p = new Paint(Paint.ANTI_ALIAS_FLAG);
        final ArrayList<Habit> habits = new ArrayList<>();
        final ArrayList<Hit> hits = new ArrayList<>();
        final SharedPreferences prefs;
        final String[] cats = {"Todos","Corpo","Mente","Projetos","Pessoal"};
        final String[] periods = {"7 dias","30 dias","90 dias","1 ano"};
        Calendar now = Calendar.getInstance(), shownMonth = Calendar.getInstance();
        float s=1f, H=800, W=390, topBar=60, bottomTop=720, contentTop=60, contentH=600, scroll=0, maxScroll=0;
        float downX, downY, startScroll; boolean dragging=false;
        int screen=0, selectedCat=0, selectedPeriod=1;
        boolean menu=false;

        OlivenView(Context ctx){
            super(ctx);
            setLayerType(View.LAYER_TYPE_SOFTWARE, null);
            prefs=ctx.getSharedPreferences("oliven", Context.MODE_PRIVATE);
            shownMonth.set(Calendar.DAY_OF_MONTH,1);
            loadHabits();
            setFocusable(true);
        }

        void loadHabits(){
            String raw=prefs.getString("habits_v3", null);
            if(raw==null) raw=prefs.getString("habits_v2", null);
            if(raw==null){
                habits.add(new Habit(1,"Academia","5x por semana","Corpo"));
                habits.add(new Habit(2,"Projeto Homem de Ferro","1h42 / 2h","Projetos"));
                habits.add(new Habit(3,"Beber água","3,2 / 3 litros","Corpo"));
                habits.add(new Habit(4,"Leitura","30 min por dia","Mente"));
                habits.add(new Habit(5,"Organização","Diário","Pessoal"));
                habits.add(new Habit(6,"Cardio","4x por semana","Corpo"));
                habits.add(new Habit(7,"Estudo","1h por dia","Mente"));
                saveHabits(); return;
            }
            habits.clear();
            for(String line: raw.split("\\n")){
                if(line.trim().isEmpty()) continue;
                String[] a=line.split("\\t",4);
                if(a.length==4){
                    try { habits.add(new Habit(Integer.parseInt(a[0]),a[1],a[2],a[3])); } catch(Exception ignored){}
                }
            }
            if(habits.isEmpty()){ prefs.edit().remove("habits_v3").apply(); loadHabits(); }
        }
        void saveHabits(){
            StringBuilder sb=new StringBuilder();
            for(Habit h:habits) sb.append(h.id).append('\t').append(h.name).append('\t').append(h.goal).append('\t').append(h.cat).append('\n');
            prefs.edit().putString("habits_v3", sb.toString()).apply();
        }

        float X(float v){return v*s;} float Y(float v){return v*s;}
        void hit(float l,float t,float r,float b,int type,int idx){ hits.add(new Hit(X(l),Y(t),X(r),Y(b),type,idx)); }
        int mainCount(){ return Math.min(5, habits.size()); }
        Calendar cal(int y,int m,int d){ Calendar c=Calendar.getInstance(); c.set(y,m,d,12,0,0); c.set(Calendar.MILLISECOND,0); return c; }
        String key(Calendar c,int id){ return "done_"+new SimpleDateFormat("yyyyMMdd",Locale.US).format(c.getTime())+"_"+id; }
        String touched(Calendar c){ return "touched_"+new SimpleDateFormat("yyyyMMdd",Locale.US).format(c.getTime()); }
        boolean done(Calendar c,int i){ return i>=0 && i<habits.size() && prefs.getBoolean(key(c,habits.get(i).id),false); }
        int doneMain(Calendar c){ int d=0; for(int i=0;i<mainCount();i++) if(done(c,i)) d++; return d; }
        int pct(Calendar c){ return mainCount()==0?0:Math.round(doneMain(c)*100f/mainCount()); }
        boolean hasData(Calendar c){ if(prefs.getBoolean(touched(c),false)) return true; for(int i=0;i<habits.size();i++) if(done(c,i)) return true; return false; }
        int monthPct(Calendar base){
            Calendar m=(Calendar)base.clone(); m.set(Calendar.DAY_OF_MONTH,1); int max=m.getActualMaximum(Calendar.DAY_OF_MONTH); int sum=0,count=0;
            for(int d=1; d<=max; d++){ Calendar c=cal(m.get(Calendar.YEAR),m.get(Calendar.MONTH),d); if(c.after(now)) break; if(hasData(c)){ sum+=pct(c); count++; } }
            return count==0 ? -1 : Math.round(sum/(float)count);
        }
        int periodPct(int days){
            Calendar c=(Calendar)now.clone(); int sum=0,count=0;
            for(int i=0;i<days;i++){ if(hasData(c)){sum+=pct(c);count++;} c.add(Calendar.DAY_OF_MONTH,-1); }
            return count==0?0:Math.round(sum/(float)count);
        }
        int monthValue(int month){ Calendar m=(Calendar)now.clone(); m.set(Calendar.MONTH,month); return monthPct(m); }
        int colorPct(int v){ if(v<=0)return Color.TRANSPARENT; int a=36 + Math.min(170, v*2); return Color.argb(a,31,111,78); }
        String monthName(Calendar c){ return new SimpleDateFormat("MMMM yyyy", new Locale("pt","BR")).format(c.getTime()); }

        void font(float z,int col,boolean bold){ p.setTypeface(Typeface.create("sans",bold?Typeface.BOLD:Typeface.NORMAL)); p.setTextSize(X(z)); p.setColor(col); p.setStyle(Paint.Style.FILL); p.clearShadowLayer(); }
        void text(Canvas c,String t,float x,float y,float z,int col,boolean bold){ font(z,col,bold); p.setTextAlign(Paint.Align.LEFT); c.drawText(t,X(x),Y(y),p); }
        void center(Canvas c,String t,float x,float y,float z,int col,boolean bold){ font(z,col,bold); p.setTextAlign(Paint.Align.CENTER); c.drawText(t,X(x),Y(y),p); p.setTextAlign(Paint.Align.LEFT); }
        void right(Canvas c,String t,float x,float y,float z,int col,boolean bold){ font(z,col,bold); p.setTextAlign(Paint.Align.RIGHT); c.drawText(t,X(x),Y(y),p); p.setTextAlign(Paint.Align.LEFT); }
        void round(Canvas c,float l,float t,float r,float b,float rad,int col){ p.setStyle(Paint.Style.FILL); p.setColor(col); p.clearShadowLayer(); c.drawRoundRect(X(l),Y(t),X(r),Y(b),X(rad),X(rad),p); }
        void card(Canvas c,float l,float t,float r,float b,float rad){ p.setStyle(Paint.Style.FILL); p.setColor(WHITE); p.setShadowLayer(X(2.2f),0,X(1.4f),0x15000000); c.drawRoundRect(X(l),Y(t),X(r),Y(b),X(rad),X(rad),p); p.clearShadowLayer(); p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(X(.7f)); p.setColor(BORDER); c.drawRoundRect(X(l),Y(t),X(r),Y(b),X(rad),X(rad),p); }
        void line(Canvas c,float x1,float y1,float x2,float y2,int col,float w){ p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(X(w)); p.setColor(col); p.setStrokeCap(Paint.Cap.ROUND); c.drawLine(X(x1),Y(y1),X(x2),Y(y2),p); }
        void iconButton(Canvas c,float cx,float cy,String glyph,int type,int idx){ card(c,cx-15,cy-15,cx+15,cy+15,9); center(c,glyph,cx,cy+5,15,TEXT,false); hit(cx-18,cy-18,cx+18,cy+18,type,idx); }

        @Override protected void onDraw(Canvas c){
            s=getWidth()/390f; W=getWidth()/s; H=getHeight()/s; hits.clear(); c.drawColor(BG);
            float safeBottom = 0;
            bottomTop = H - safeBottom - 74;
            topBar = 64;
            contentTop = topBar;
            contentH = Math.max(260, bottomTop - contentTop);
            if(scroll>maxScroll) scroll=maxScroll;
            drawContent(c);
            drawTopBar(c);
            drawBottomBar(c);
            if(menu) drawMenu(c);
        }

        void drawContent(Canvas c){
            if(screen==0) drawHome(c); else if(screen==1) drawProgress(c); else if(screen==2) drawHabits(c); else if(screen==3) drawProfile(c); else if(screen==4) drawCalendarCircle(c); else drawYearInsights(c);
        }

        void drawTopBar(Canvas c){
            p.setStyle(Paint.Style.FILL); p.setColor(WHITE); c.drawRect(0,0,X(390),Y(topBar),p);
            p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(X(.7f)); p.setColor(BORDER); c.drawLine(0,Y(topBar),X(390),Y(topBar),p);
            drawOlivenSymbol(c,18,14,32); text(c,"Oliven",58,38,17,TEXT,true);
            iconButton(c,327,31,"◇",10,0); iconButton(c,363,31,"☰",1,0);
        }
        void drawBottomBar(Canvas c){
            p.setStyle(Paint.Style.FILL); p.setColor(WHITE); c.drawRect(0,Y(bottomTop),X(390),Y(H),p);
            p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(X(.7f)); p.setColor(BORDER); c.drawLine(0,Y(bottomTop),X(390),Y(bottomTop),p);
            String[] labels={"Início","Progresso","Hábitos","Perfil"}; String[] icons={"⌂","↗","✓","♙"};
            for(int i=0;i<4;i++){
                float cx=49+i*97; boolean active=(screen==i);
                if(active) round(c,cx-44,bottomTop+10,cx+44,bottomTop+64,16,SOFT);
                center(c,icons[i],cx,bottomTop+31,22,active?GREEN:MUTED,true);
                center(c,labels[i],cx,bottomTop+54,10,active?GREEN:MUTED,active);
                hit(cx-48,bottomTop+4,cx+48,bottomTop+70,2,i);
            }
        }
        void drawOlivenSymbol(Canvas c,float x,float y,float size){
            round(c,x,y,x+size,y+size,8,BLACK);
            p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(X(size*.075f)); p.setStrokeCap(Paint.Cap.BUTT); p.setColor(OLIVE);
            RectF rr=new RectF(X(x+size*.12f),Y(y+size*.15f),X(x+size*.88f),Y(y+size*.85f));
            c.drawArc(rr,200,140,false,p); c.drawArc(rr,20,140,false,p);
            p.setStrokeCap(Paint.Cap.ROUND); p.setStrokeWidth(X(size*.055f));
            c.drawLine(X(x+size*.12f),Y(y+size*.50f),X(x+size*.36f),Y(y+size*.50f),p);
            c.drawLine(X(x+size*.64f),Y(y+size*.50f),X(x+size*.88f),Y(y+size*.50f),p);
            p.setStyle(Paint.Style.FILL); p.setColor(OLIVE);
            float cy=y+size*.50f; c.drawCircle(X(x+size*.13f),Y(cy),X(size*.055f),p); c.drawCircle(X(x+size*.36f),Y(cy),X(size*.065f),p); c.drawCircle(X(x+size*.64f),Y(cy),X(size*.065f),p); c.drawCircle(X(x+size*.87f),Y(cy),X(size*.055f),p);
        }

        void header(Canvas c,String title,String sub,float y){ text(c,title,20,y,24,TEXT,true); if(sub!=null) text(c,sub,20,y+24,10.5f,MUTED,false); }
        void drawHome(Canvas c){
            float y=contentTop+scroll*-1+38; header(c,"Olá, Jean.","16/08/2026 · Evolução pessoal",y);
            int today=pct(now); float cy=y+145; drawSegmentCircle(c,195,cy,118,60,today,false); center(c,today+"%",195,cy+11,38,TEXT,true); center(c,"Consistência de hoje",195,cy+39,10.5f,MUTED,false); hit(58,cy-125,332,cy+125,10,0);
            float top=cy+176, bottom=top+245; card(c,14,top,376,bottom,18); text(c,"HOJE",28,top+31,12,TEXT,true); right(c,doneMain(now)+" de "+mainCount()+" concluídos",358,top+31,11,GREEN,true);
            float row=(bottom-top-54)/mainCount(); for(int i=0;i<mainCount();i++){ float yy=top+60+i*row; check(c,40,yy-3,done(now,i)); text(c,habits.get(i).name,58,yy-8,13,TEXT,true); text(c,habits.get(i).goal,58,yy+9,8.5f,MUTED,false); hit(25,yy-row*.45f,365,yy+row*.45f,3,i); }
            float it=bottom+16; round(c,14,it,376,it+62,16,SOFT); text(c,"↗",30,it+38,15,GREEN,true); text(c,"Seu ritmo está ficando mais consistente",58,it+30,12,TEXT,true); text(c,"Toque para ver Meu ano e insights",58,it+47,8.5f,MUTED,false); hit(14,it,376,it+62,10,1);
            maxScroll=Math.max(0,it+82-contentH-contentTop);
        }
        void drawSegmentCircle(Canvas c,float cx,float cy,float r,int seg,int value,boolean month){
            RectF rr=new RectF(X(cx-r),Y(cy-r),X(cx+r),Y(cy+r)); p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(X(month?8.5f:8f)); p.setStrokeCap(Paint.Cap.ROUND);
            for(int i=0;i<seg;i++){
                float start=-90+i*(360f/seg); float sweep=(360f/seg)*.46f; p.setColor(LIGHT); c.drawArc(rr,start,sweep,false,p);
                float percent=value/100f; if(percent>0){ float filled;
                    if(month) filled=percent; else filled=(i < Math.round(seg*percent))?1:0;
                    if(filled>0){ p.setColor(GREEN); c.drawArc(rr,start,sweep*filled,false,p); }
                }
            }
        }
        void check(Canvas c,float x,float y,boolean d){ p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(X(1.3f)); p.setColor(d?GREEN:MUTED); c.drawCircle(X(x),Y(y),X(6f),p); if(d){p.setStyle(Paint.Style.FILL);p.setColor(GREEN);c.drawCircle(X(x),Y(y),X(4.8f),p);} }

        void drawProgress(Canvas c){
            float y=contentTop-scroll+35; center(c,"Progresso",195,y,18,TEXT,true);
            for(int i=0;i<4;i++){ float l=18+i*88; round(c,l,y+18,l+80,y+47,16,i==selectedPeriod?SOFT:WHITE); center(c,periods[i],l+40,y+37,8.5f,i==selectedPeriod?TEXT:MUTED,i==selectedPeriod); hit(l,y+18,l+80,y+47,5,i); }
            int pv=selectedPeriod==0?periodPct(7):selectedPeriod==1?periodPct(30):selectedPeriod==2?periodPct(90):periodPct(365);
            card(c,16,y+63,374,y+242,18); text(c,"Taxa de consistência",30,y+91,10,MUTED,false); text(c,pv+"%",30,y+130,30,TEXT,true); text(c,"↑ 8% vs período anterior",30,y+154,10,GREEN,false); drawLineChart(c,30,y+180,360,y+225);
            card(c,16,y+260,374,y+386,18); text(c,"Resumo",30,y+289,13,TEXT,true); String[] rs={"Hoje","Semana","Mês","Últimos 90 dias"}; int[] vals={pct(now),periodPct(7),Math.max(0,monthPct(now)),periodPct(90)}; for(int i=0;i<4;i++){ text(c,rs[i],30,y+319+i*21,9.5f,TEXT,false); right(c,vals[i]+"%",356,y+319+i*21,9.5f,GREEN,true); }
            card(c,16,y+404,374,y+486,18); text(c,"Tendência",30,y+432,10,MUTED,false); text(c,"↑ 8%",30,y+461,20,GREEN,true); text(c,"Melhor que o mês anterior",30,y+480,9,MUTED,false);
            maxScroll=Math.max(0,y+510-contentH-contentTop);
        }
        void drawLineChart(Canvas c,float l,float t,float r,float b){ for(int i=0;i<3;i++) line(c,l,t+i*(b-t)/2,r,t+i*(b-t)/2,BORDER,.55f); Path path=new Path(); for(int i=0;i<10;i++){ float xx=l+i*(r-l)/9; float yy=b-(i*5+(i%3)*5); if(i==0) path.moveTo(X(xx),Y(yy)); else path.lineTo(X(xx),Y(yy)); } p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(X(2.2f)); p.setColor(GREEN); p.setStrokeCap(Paint.Cap.ROUND); c.drawPath(path,p); }

        void drawHabits(Canvas c){
            float y=contentTop-scroll+42; text(c,"Hábitos",20,y,26,TEXT,true); text(c,"Meus hábitos",20,y+23,10,MUTED,false); text(c,"+",355,y,24,TEXT,true); hit(330,y-34,380,y+15,7,0);
            for(int i=0;i<cats.length;i++){ float l=18+i*71; round(c,l,y+39,l+66,y+66,14,i==selectedCat?SOFT:WHITE); center(c,cats[i],l+33,y+57,8.3f,i==selectedCat?GREEN:MUTED,i==selectedCat); hit(l,y+39,l+66,y+66,6,i); }
            float top=y+82; int n=0; for(int i=0;i<habits.size();i++){ Habit h=habits.get(i); if(selectedCat>0 && !h.cat.equals(cats[selectedCat])) continue; float yy=top+n*63; card(c,16,yy,374,yy+52,16); round(c,30,yy+10,64,yy+44,10,SOFT2); center(c,symbolFor(h.cat),47,yy+32,13,GREEN,true); text(c,h.name,78,yy+25,12.5f,TEXT,true); text(c,h.goal,78,yy+41,8.5f,MUTED,false); center(c,"⋮",348,yy+33,18,MUTED,true); n++; }
            maxScroll=Math.max(0,top+n*63+20-contentH-contentTop);
        }
        String symbolFor(String cat){ if(cat.equals("Corpo")) return "●"; if(cat.equals("Mente")) return "▤"; if(cat.equals("Projetos")) return "◆"; return "✓"; }

        void drawProfile(Canvas c){
            float y=contentTop-scroll+35; center(c,"Perfil",195,y,18,TEXT,true);
            card(c,16,y+22,374,y+92,18); round(c,30,y+36,78,y+84,24,GREEN); center(c,"J",54,y+68,22,WHITE,true); text(c,"Jean Silva",96,y+55,13,TEXT,true); text(c,"Membro desde abr/2024",96,y+72,8.5f,MUTED,false);
            String[][] rows={{"Dados pessoais","Nome, preferências e objetivo"},{"Preferências","Aparência e rotina"},{"Notificações","Lembretes da rotina"},{"Backup e sincronização","Em breve"},{"Ajuda e suporte","Central de ajuda"},{"Sobre a Oliven","Oliven 1.0.12 · Android nativo"}};
            for(int i=0;i<rows.length;i++){ float yy=y+108+i*58; card(c,16,yy,374,yy+48,15); text(c,30,rows[i][0],yy+25); }
            maxScroll=Math.max(0,y+108+rows.length*58+20-contentH-contentTop);
        }
        void text(Canvas c,float x,String t,float y){ text(c,t,x,y,11.5f,TEXT,true); }

        void drawCalendarCircle(Canvas c){
            float y=contentTop-scroll+30; center(c,"Calendário e Círculo",195,y,17,TEXT,true); text(c,"‹",28,y+2,20,TEXT,false); text(c,"›",354,y+2,20,TEXT,false); center(c,monthName(shownMonth),195,y+30,10.5f,TEXT,true); hit(14,y-18,60,y+45,9,-1); hit(330,y-18,380,y+45,9,1);
            float calTop=y+48; card(c,14,calTop,376,calTop+190,16); drawCalendar(c,32,calTop+26,358,calTop+170,shownMonth);
            float ringTop=calTop+204; card(c,14,ringTop,376,ringTop+190,16); drawMonthRing(c,195,ringTop+94,74,shownMonth);
            float habitsTop=ringTop+204; card(c,14,habitsTop,376,habitsTop+145,16); text(c,"Hábitos do dia",28,habitsTop+28,12,TEXT,true); right(c,doneMain(now)+" de "+mainCount()+" concluídos",358,habitsTop+28,10,GREEN,true); for(int i=0;i<mainCount();i++){ float yy=habitsTop+53+i*17; check(c,36,yy-3,done(now,i)); text(c,54,habits.get(i).name,yy); }
            float consTop=habitsTop+158; card(c,14,consTop,376,consTop+70,16); int mp=monthPct(shownMonth); text(c,"Consistência do mês",28,consTop+31,12,TEXT,true); text(c,mp<0?"-":mp+"%",302,consTop+41,24,GREEN,true); text(c,"Baseada nos check-ins salvos",28,consTop+50,8.5f,MUTED,false);
            maxScroll=Math.max(0,consTop+86-contentH-contentTop);
        }
        void drawCalendar(Canvas c,float l,float t,float r,float b,Calendar month){
            String[] ds={"D","S","T","Q","Q","S","S"}; float cell=(r-l)/7f; for(int i=0;i<7;i++) center(c,ds[i],l+cell*i+cell/2,t,8.5f,MUTED,false);
            Calendar m=(Calendar)month.clone(); m.set(Calendar.DAY_OF_MONTH,1); int first=m.get(Calendar.DAY_OF_WEEK)-1; int max=m.getActualMaximum(Calendar.DAY_OF_MONTH); float rowH=(b-t-18)/6f;
            for(int d=1;d<=max;d++){ int pos=first+d-1; int col=pos%7,row=pos/7; float cx=l+cell*col+cell/2, cy=t+18+row*rowH; Calendar day=cal(m.get(Calendar.YEAR),m.get(Calendar.MONTH),d); int pc=pct(day); if(!day.after(now) && (hasData(day)||d==now.get(Calendar.DAY_OF_MONTH))) round(c,cx-12,cy-12,cx+12,cy+12,10,colorPct(pc)); center(c,String.valueOf(d),cx,cy+4,8.5f,(pc>=60?GREEN:TEXT),pc>=80); }
        }
        void drawMonthRing(Canvas c,float cx,float cy,float r,Calendar month){
            Calendar m=(Calendar)month.clone(); m.set(Calendar.DAY_OF_MONTH,1); int max=m.getActualMaximum(Calendar.DAY_OF_MONTH); RectF rr=new RectF(X(cx-r),Y(cy-r),X(cx+r),Y(cy+r)); p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(X(10)); p.setStrokeCap(Paint.Cap.ROUND);
            for(int d=1;d<=max;d++){ float start=-90+(d-1)*360f/max; float sweep=360f/max*.45f; Calendar day=cal(m.get(Calendar.YEAR),m.get(Calendar.MONTH),d); int pc=pct(day); p.setColor(LIGHT); c.drawArc(rr,start,sweep,false,p); if(!day.after(now)&&pc>0){ p.setColor(GREEN2); c.drawArc(rr,start,sweep*(pc/100f),false,p); } if(d%2==1) center(c,String.valueOf(d),cx+(float)Math.cos(Math.toRadians(start+2))*X(0)/s,cy,1,Color.TRANSPARENT,false); }
            center(c,String.valueOf(now.get(Calendar.DAY_OF_MONTH)),cx,cy-1,30,TEXT,true); center(c,new SimpleDateFormat("MMM",new Locale("pt","BR")).format(now.getTime()).toUpperCase(),cx,cy+23,9,MUTED,true);
        }

        void drawYearInsights(Canvas c){
            float y=contentTop-scroll+30; center(c,"Meu ano",195,y,18,TEXT,true); text(c,"‹",28,y+2,20,TEXT,false); text(c,"›",354,y+2,20,TEXT,false); center(c,"2026",195,y+31,11,MUTED,true);
            float gridTop=y+60; String[] ms={"JAN","FEV","MAR","ABR","MAI","JUN","JUL","AGO","SET","OUT","NOV","DEZ"};
            for(int i=0;i<12;i++){ int row=i/4,col=i%4; float cx=58+col*92, cy=gridTop+row*80; int val=monthValue(i); center(c,ms[i],cx,cy-28,8,MUTED,true); monthBubble(c,cx,cy,val); }
            float insTop=gridTop+235; card(c,14,insTop,376,insTop+230,18); text(c,"Insights da Oliven",28,insTop+29,13,TEXT,true); String[][] ins={{"Você é mais consistente nas segundas e terças.","Taxa média nesses dias: 87%"},{"Suas noites após as 21h têm menor conclusão.","Considere ajustar sua rotina."},{"Seu desempenho geral melhorou 8% este mês.","Continue evoluindo!"},{"A água costuma ficar para o fim do dia.","Antecipe esse hábito pela manhã."}}; for(int i=0;i<ins.length;i++){ float yy=insTop+58+i*40; round(c,28,yy-22,58,yy+8,10,SOFT2); center(c,i==1?"◷":"↗",43,yy,13,GREEN,true); text(c,70,ins[i][0],yy-4); text(c,ins[i][1],70,yy+14,8.5f,MUTED,false); }
            maxScroll=Math.max(0,insTop+250-contentH-contentTop);
        }
        void monthBubble(Canvas c,float cx,float cy,int v){ p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(X(2.2f)); p.setColor(v<0?BORDER:GREEN); c.drawCircle(X(cx),Y(cy),X(25),p); center(c,v<0?"-":v+"%",cx,cy+4,9,TEXT,true); }

        void drawMenu(Canvas c){
            p.setStyle(Paint.Style.FILL); p.setColor(0x70000000); c.drawRect(0,0,X(390),Y(H),p);
            card(c,36,98,354,440,18); text(c,"Oliven",64,132,22,TEXT,true); String[] opts={"Tela Inicial","Evolução","Calendário + Círculo","Meu ano + Insights","Hábitos","Perfil"}; int[] screens={0,1,4,5,2,3}; for(int i=0;i<opts.length;i++){ float yy=168+i*42; text(c,opts[i],64,yy,15,TEXT,false); hit(50,yy-27,340,yy+11,8,screens[i]); }
        }

        @Override public boolean onTouchEvent(android.view.MotionEvent e){
            float x=e.getX(), y=e.getY();
            if(e.getAction()==MotionEvent.ACTION_DOWN){ downX=x; downY=y; startScroll=scroll; dragging=false; return true; }
            if(e.getAction()==MotionEvent.ACTION_MOVE){ float dy=(y-downY)/s; if(Math.abs(dy)>4){ dragging=true; scroll=Math.max(0,Math.min(maxScroll,startScroll-dy)); invalidate(); } return true; }
            if(e.getAction()==MotionEvent.ACTION_UP){ if(dragging){ return true; } for(Hit h:hits){ if(h.r.contains(x,y)){ action(h.type,h.index); return true; } } if(menu){ menu=false; invalidate(); return true; } return true; }
            return true;
        }
        void action(int type,int idx){
            if(type==1){ menu=true; invalidate(); return; }
            if(type==2){ screen=idx; scroll=0; menu=false; invalidate(); return; }
            if(type==3){ Calendar c=(Calendar)now.clone(); prefs.edit().putBoolean(key(c,habits.get(idx).id),!done(c,idx)).putBoolean(touched(c),true).apply(); invalidate(); return; }
            if(type==5){ selectedPeriod=idx; invalidate(); return; }
            if(type==6){ selectedCat=idx; scroll=0; invalidate(); return; }
            if(type==7){ addHabit(); return; }
            if(type==8){ screen=idx; scroll=0; menu=false; invalidate(); return; }
            if(type==9){ shownMonth.add(Calendar.MONTH,idx); scroll=0; invalidate(); return; }
            if(type==10){ screen=idx; scroll=0; invalidate(); return; }
        }
        void addHabit(){
            final EditText nome=new EditText(getContext()); nome.setHint("Nome do hábito");
            final EditText meta=new EditText(getContext()); meta.setHint("Meta");
            LinearLayout box=new LinearLayout(getContext()); box.setOrientation(LinearLayout.VERTICAL); int pad=(int)X(18); box.setPadding(pad,pad,pad,0); box.addView(nome); box.addView(meta);
            new AlertDialog.Builder(getContext()).setTitle("Novo hábito").setView(box).setNegativeButton("Cancelar",null).setPositiveButton("Adicionar",(d,w)->{ String n=nome.getText().toString().trim(); String m=meta.getText().toString().trim(); if(n.length()==0)n="Novo hábito"; if(m.length()==0)m="Diário"; int id=(int)(System.currentTimeMillis()%1000000); habits.add(new Habit(id,n,m,"Pessoal")); saveHabits(); selectedCat=0; invalidate(); }).show();
        }
    }
}
