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
        getWindow().setStatusBarColor(Color.rgb(250,251,248));
        getWindow().setNavigationBarColor(Color.WHITE);
        if (Build.VERSION.SDK_INT >= 23) getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR | View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR);
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
        final int BG=Color.rgb(250,251,248), WHITE=Color.WHITE, TEXT=Color.rgb(25,31,26), MUTED=Color.rgb(103,110,105);
        final int GREEN=Color.rgb(31,111,78), GREEN2=Color.rgb(84,166,96), OLIVE=Color.rgb(116,138,53), SOFT=Color.rgb(239,246,237), BORDER=Color.rgb(224,229,222), LIGHT=Color.rgb(232,238,231);
        final Paint p = new Paint(Paint.ANTI_ALIAS_FLAG);
        final ArrayList<Habit> habits = new ArrayList<>();
        final ArrayList<Hit> hits = new ArrayList<>();
        final SharedPreferences prefs;
        final String[] cats = {"Todos","Corpo","Mente","Projetos","Pessoal"};
        final String[] periods = {"7 dias","30 dias","90 dias","1 ano"};
        Calendar now = Calendar.getInstance(), shownMonth = Calendar.getInstance();
        float s=1f, H=780, navTop=700;
        int screen=0, selectedCat=0, selectedPeriod=1;
        boolean menu=false;

        OlivenView(Context ctx){
            super(ctx); setLayerType(View.LAYER_TYPE_SOFTWARE, null); prefs=ctx.getSharedPreferences("oliven", Context.MODE_PRIVATE);
            shownMonth.set(Calendar.DAY_OF_MONTH,1); loadHabits(); setFocusable(true);
        }

        void loadHabits(){
            String raw=prefs.getString("habits_v2", null);
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
                if(a.length==4) habits.add(new Habit(Integer.parseInt(a[0]),a[1],a[2],a[3]));
            }
            if(habits.isEmpty()) { prefs.edit().remove("habits_v2").apply(); loadHabits(); }
        }
        void saveHabits(){
            StringBuilder sb=new StringBuilder();
            for(Habit h:habits) sb.append(h.id).append('\t').append(h.name).append('\t').append(h.goal).append('\t').append(h.cat).append('\n');
            prefs.edit().putString("habits_v2", sb.toString()).apply();
        }

        float X(float v){return v*s;} float Y(float v){return v*s;}
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
        int colorPct(int v){ if(v<=0)return Color.TRANSPARENT; int a=55 + Math.min(180, v*2); return Color.argb(a,31,111,78); }
        int textColorForPct(int v){ return v>=60?WHITE:GREEN; }

        void font(float z,int col,boolean bold){ p.setTypeface(Typeface.create("sans",bold?Typeface.BOLD:Typeface.NORMAL)); p.setTextSize(X(z)); p.setColor(col); p.setStyle(Paint.Style.FILL); p.clearShadowLayer(); }
        void text(Canvas c,String t,float x,float y,float z,int col,boolean bold){ font(z,col,bold); p.setTextAlign(Paint.Align.LEFT); c.drawText(t,X(x),Y(y),p); }
        void center(Canvas c,String t,float x,float y,float z,int col,boolean bold){ font(z,col,bold); p.setTextAlign(Paint.Align.CENTER); c.drawText(t,X(x),Y(y),p); p.setTextAlign(Paint.Align.LEFT); }
        void round(Canvas c,float l,float t,float r,float b,float rad,int col){ p.setStyle(Paint.Style.FILL); p.setColor(col); p.clearShadowLayer(); c.drawRoundRect(X(l),Y(t),X(r),Y(b),X(rad),X(rad),p); }
        void card(Canvas c,float l,float t,float r,float b,float rad){ p.setStyle(Paint.Style.FILL); p.setColor(WHITE); p.setShadowLayer(X(2),0,X(1.4f),0x13000000); c.drawRoundRect(X(l),Y(t),X(r),Y(b),X(rad),X(rad),p); p.clearShadowLayer(); p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(X(.7f)); p.setColor(BORDER); c.drawRoundRect(X(l),Y(t),X(r),Y(b),X(rad),X(rad),p); }
        void line(Canvas c,float x1,float y1,float x2,float y2,int col,float w){ p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(X(w)); p.setColor(col); p.setStrokeCap(Paint.Cap.ROUND); c.drawLine(X(x1),Y(y1),X(x2),Y(y2),p); }
        void hamburger(Canvas c,float x,float y){ for(int i=0;i<3;i++) line(c,x,y+i*7,x+17,y+i*7,TEXT,1.5f); hits.add(new Hit(X(x-12),Y(y-16),X(x+38),Y(y+35),1,0)); }
        void check(Canvas c,float x,float y,boolean d){ p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(X(1.2f)); p.setColor(d?GREEN:MUTED); c.drawCircle(X(x),Y(y),X(5.7f),p); if(d){p.setStyle(Paint.Style.FILL);p.setColor(GREEN);c.drawCircle(X(x),Y(y),X(4.4f),p);} }
        void logo(Canvas c,float x,float y,float size,boolean full){
            p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(size*.075f*s); p.setStrokeCap(Paint.Cap.BUTT); p.setColor(OLIVE);
            RectF rr=new RectF(X(x),Y(y),X(x+size),Y(y+size)); c.drawArc(rr,200,140,false,p); c.drawArc(rr,20,140,false,p);
            p.setStrokeWidth(size*.06f*s); p.setStrokeCap(Paint.Cap.ROUND); line(c,x+size*.08f,y+size*.5f,x+size*.35f,y+size*.5f,OLIVE,size*.06f); line(c,x+size*.65f,y+size*.5f,x+size*.92f,y+size*.5f,OLIVE,size*.06f);
            p.setStyle(Paint.Style.FILL); p.setColor(OLIVE); float cy=y+size*.5f; c.drawCircle(X(x+size*.08f),Y(cy),X(size*.06f),p); c.drawCircle(X(x+size*.35f),Y(cy),X(size*.06f),p); c.drawCircle(X(x+size*.65f),Y(cy),X(size*.06f),p); c.drawCircle(X(x+size*.92f),Y(cy),X(size*.06f),p);
            if(full) text(c,"Oliven",x+size+8,y+size*.67f,18,GREEN,true);
        }

        @Override protected void onDraw(Canvas c){
            s=getWidth()/390f; H=getHeight()/s; navTop=H-78; hits.clear(); c.drawColor(BG);
            if(screen==0) home(c); else if(screen==1) progress(c); else if(screen==2) habitsPage(c); else if(screen==3) profile(c); else if(screen==4) circlePage(c); else if(screen==5) myDay(c); else if(screen==6) calendarPage(c); else if(screen==7) insightsPage(c); else yearPage(c);
            bottom(c); if(menu) drawer(c);
        }

        void home(Canvas c){
            hamburger(c,22,24); logo(c,320,22,26,false); text(c,"Bom dia, Jean",20,76,24,TEXT,true); text(c,"Domingo, 16 de agosto",20,97,10.5f,MUTED,false);
            float cy=222; bigRing(c,195,cy,105,pct(now)); center(c,pct(now)+"%",195,cy+10,38,TEXT,true); center(c,"Consistência de hoje",195,cy+34,10,MUTED,false); hits.add(new Hit(X(82),Y(cy-116),X(308),Y(cy+116),4,0));
            float top=365,b=navTop-118; if(b<610)b=610; card(c,18,top,372,b,18); text(c,"HOJE",32,top+29,12,TEXT,true); text(c,doneMain(now)+" de "+mainCount()+" concluídos",282,top+29,10.5f,GREEN,true);
            float row=(b-top-49)/mainCount(); for(int i=0;i<mainCount();i++){ float yy=top+56+i*row; check(c,42,yy-4,done(now,i)); text(c,habits.get(i).name,60,yy-8,13,TEXT,true); text(c,habits.get(i).goal,60,yy+8,8.5f,MUTED,false); hits.add(new Hit(X(24),Y(yy-row*.48f),X(368),Y(yy+row*.48f),3,i)); }
            float it=b+15; round(c,18,it,372,it+62,17,SOFT); text(c,"↗",32,it+38,15,GREEN,true); text(c,"Seu ritmo está ficando mais consistente",60,it+29,12,TEXT,true); text(c,"Toque para ver os insights da Oliven",60,it+45,8.5f,MUTED,false); hits.add(new Hit(X(18),Y(it),X(372),Y(it+62),11,0));
        }
        void bigRing(Canvas c,float cx,float cy,float r,int value){
            RectF rr=new RectF(X(cx-r),Y(cy-r),X(cx+r),Y(cy+r)); p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(X(7.5f)); p.setStrokeCap(Paint.Cap.BUTT); int fill=Math.round(value*.6f);
            for(int i=0;i<60;i++){ p.setColor(i<fill?GREEN2:LIGHT); c.drawArc(rr,-90+i*6,4.2f,false,p); } p.setStrokeCap(Paint.Cap.ROUND);
        }

        void progress(Canvas c){
            hamburger(c,22,24); center(c,"Evolução",195,40,18,TEXT,true);
            for(int i=0;i<4;i++){ float l=18+i*88; round(c,l,62,l+80,90,16,i==selectedPeriod?SOFT:WHITE); center(c,periods[i],l+40,81,8.5f,i==selectedPeriod?TEXT:MUTED,i==selectedPeriod); hits.add(new Hit(X(l),Y(62),X(l+80),Y(90),5,i)); }
            int pv = selectedPeriod==0?periodPct(7):selectedPeriod==1?periodPct(30):selectedPeriod==2?periodPct(90):periodPct(365);
            card(c,18,105,372,282,18); text(c,"Taxa de consistência",30,132,10,MUTED,false); text(c,pv+"%",30,170,28,TEXT,true); text(c,"↑ evolução do seu ritmo",30,193,10,GREEN,true); for(int i=0;i<4;i++) line(c,30,218+i*15,358,218+i*15,BORDER,.55f);
            Path path=new Path(); for(int i=0;i<10;i++){ float xx=30+i*36.5f; float yy=263-(i*9 + (i%3)*7); if(i==0) path.moveTo(X(xx),Y(yy)); else path.lineTo(X(xx),Y(yy)); } p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(X(2.2f)); p.setColor(GREEN); c.drawPath(path,p);
            card(c,18,298,372,418,18); text(c,"Resumo",30,326,12,TEXT,true); String[] rs={"Hoje","Semana","Mês","Últimos 90 dias"}; int[] vals={pct(now),periodPct(7),Math.max(0,monthPct(now)),periodPct(90)}; for(int i=0;i<4;i++){ text(c,rs[i],30,352+i*18,9,TEXT,false); text(c,vals[i]+"%",340,352+i*18,9,GREEN,true); }
            drawMiniCalendar(c,18,435,372,585);
            drawMiniInsights(c,18,600,372,690);
            drawMiniYear(c,18,704,372,navTop-8);
        }
        void drawMiniCalendar(Canvas c,float l,float t,float r,float b){ card(c,l,t,r,b,18); text(c,"Calendário",l+12,t+25,12,TEXT,true); center(c,monthName(shownMonth),195,t+25,10,TEXT,true); text(c,"‹",l+16,t+25,16,TEXT,false); text(c,"›",r-24,t+25,16,TEXT,false); hits.add(new Hit(X(l+5),Y(t+2),X(l+45),Y(t+42),12,-1)); hits.add(new Hit(X(r-50),Y(t+2),X(r-5),Y(t+42),12,1)); drawCalendarGrid(c,l+18,t+45,r-18,b-20,shownMonth,true); }
        void drawCalendarGrid(Canvas c,float l,float t,float r,float b,Calendar m,boolean compact){
            String[] wk={"D","S","T","Q","Q","S","S"}; float cw=(r-l)/7f; for(int i=0;i<7;i++) center(c,wk[i],l+cw*i+cw/2,t,7.5f,MUTED,false);
            Calendar tmp=(Calendar)m.clone(); tmp.set(Calendar.DAY_OF_MONTH,1); int start=tmp.get(Calendar.DAY_OF_WEEK)-1, max=tmp.getActualMaximum(Calendar.DAY_OF_MONTH); float rh=(b-t-16)/6f; int d=1;
            for(int row=0;row<6;row++) for(int col=0;col<7;col++){ if(row==0&&col<start) continue; if(d>max) continue; float x=l+cw*col+cw/2, y=t+18+rh*row; Calendar dc=cal(m.get(Calendar.YEAR),m.get(Calendar.MONTH),d); int v=pct(dc); boolean data=hasData(dc); if(data){ p.setStyle(Paint.Style.FILL); p.setColor(colorPct(v)); c.drawCircle(X(x),Y(y-4),X(compact?10:14),p); } boolean today=sameDay(dc,now); center(c,""+d,x,y,compact?7.5f:9,today?GREEN:(data&&v>=70?WHITE:MUTED),today||data&&v>=70); d++; }
        }
        boolean sameDay(Calendar a,Calendar b){return a.get(Calendar.YEAR)==b.get(Calendar.YEAR)&&a.get(Calendar.MONTH)==b.get(Calendar.MONTH)&&a.get(Calendar.DAY_OF_MONTH)==b.get(Calendar.DAY_OF_MONTH);}        
        String monthName(Calendar c){ String[] m={"Janeiro","Fevereiro","Março","Abril","Maio","Junho","Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"}; return m[c.get(Calendar.MONTH)]+" "+c.get(Calendar.YEAR); }
        void drawMiniInsights(Canvas c,float l,float t,float r,float b){ card(c,l,t,r,b,18); text(c,"Insights da Oliven",l+12,t+24,12,TEXT,true); text(c,"↗",l+14,t+52,13,GREEN,true); text(c,"Você é mais consistente nas segundas e terças.",l+42,t+50,8.5f,TEXT,true); text(c,"◷",l+14,t+75,12,GREEN,true); text(c,"Noites após as 21h têm menor conclusão.",l+42,t+74,8.5f,TEXT,true); }
        void drawMiniYear(Canvas c,float l,float t,float r,float b){ if(b<t+80)return; card(c,l,t,r,b,18); text(c,"Meu ano",l+12,t+24,12,TEXT,true); float x=l+57; for(int i=0;i<4;i++){ Calendar m=Calendar.getInstance(); m.set(Calendar.MONTH,i); m.set(Calendar.DAY_OF_MONTH,1); int val=monthPct(m); center(c,(i+1)+"",x+i*75,t+52,7,MUTED,true); center(c,val<0?"-":val+"%",x+i*75,t+72,9,val<0?MUTED:GREEN,true); } }

        void habitsPage(Canvas c){
            text(c,"Hábitos",18,50,25,TEXT,true); text(c,"Meus hábitos",18,69,10,MUTED,false); text(c,"+",348,53,24,TEXT,true); hits.add(new Hit(X(330),Y(25),X(380),Y(70),7,0));
            for(int i=0;i<cats.length;i++){ float l=18+i*70; round(c,l,82,l+64,109,15,i==selectedCat?SOFT:WHITE); center(c,cats[i],l+32,100,8.3f,i==selectedCat?GREEN:MUTED,i==selectedCat); hits.add(new Hit(X(l),Y(82),X(l+64),Y(109),6,i)); }
            ArrayList<Habit> list=new ArrayList<>(); for(Habit h:habits) if(selectedCat==0 || h.cat.equals(cats[selectedCat])) list.add(h);
            String[] ic={"◉","◆","●","▤","✓","♥","▤","○","□"}; for(int i=0;i<Math.min(8,list.size());i++){ Habit h=list.get(i); float t=124+i*56; card(c,18,t,372,t+49,15); round(c,30,t+8,64,t+42,11,SOFT); center(c,ic[i%ic.length],47,t+30,11,(h.name.toLowerCase().contains("cardio")?Color.rgb(232,64,76):GREEN),true); text(c,h.name,78,t+24,11.5f,TEXT,true); text(c,h.goal,78,t+38,8,MUTED,false); text(c,"⋮",346,t+31,15,MUTED,false); }
        }

        void profile(Canvas c){ hamburger(c,22,24); center(c,"Perfil",195,40,18,TEXT,true); card(c,18,58,372,132,18); p.setStyle(Paint.Style.FILL); p.setColor(GREEN); c.drawCircle(X(58),Y(95),X(25),p); center(c,"J",58,104,22,WHITE,true); text(c,"Jean Silva",95,91,13,TEXT,true); text(c,"Membro desde abr/2024",95,107,8,MUTED,false); String[][] rows={{"Dados pessoais","Nome, preferências e objetivo"},{"Preferências","Aparência e rotina"},{"Notificações","Lembretes da rotina"},{"Backup e sincronização","Em breve"},{"Ajuda e suporte","Central de ajuda"},{"Sobre a Oliven","Oliven 1.0.10 · Android nativo"}}; float t=148; for(String[] r:rows){ card(c,18,t,372,t+54,15); text(c,r[0],30,t+25,11,TEXT,true); text(c,r[1],30,t+40,8,MUTED,false); text(c,"›",344,t+36,18,MUTED,false); t+=63; } }

        void circlePage(Canvas c){
            text(c,"‹",18,40,24,TEXT,false); hits.add(new Hit(X(0),Y(12),X(52),Y(55),8,0)); center(c,"Círculo",195,42,18,TEXT,true); center(c,monthName(shownMonth),195,75,11,TEXT,true); text(c,"‹",28,75,20,TEXT,false); text(c,"›",352,75,20,TEXT,false); hits.add(new Hit(X(18),Y(54),X(70),Y(91),9,-1)); hits.add(new Hit(X(320),Y(54),X(382),Y(91),9,1));
            float cx=195,cy=214,r=102; int max=shownMonth.getActualMaximum(Calendar.DAY_OF_MONTH); for(int i=1;i<=max;i++){ double a=Math.toRadians(-90+(i-1)*(360.0/max)); float x=(float)(cx+Math.cos(a)*r), y=(float)(cy+Math.sin(a)*r); float total=29, prog=total*(pct(cal(shownMonth.get(Calendar.YEAR),shownMonth.get(Calendar.MONTH),i))/100f); boolean data=hasData(cal(shownMonth.get(Calendar.YEAR),shownMonth.get(Calendar.MONTH),i)); c.save(); c.rotate((float)Math.toDegrees(a)+90,X(x),Y(y)); round(c,x-5.5f,y-total/2,x+5.5f,y+total/2,2,LIGHT); if(data&&prog>0) round(c,x-5.5f,y+total/2-prog,x+5.5f,y+total/2,2,GREEN2); c.restore(); if(i%2==1){ float tx=(float)(cx+Math.cos(a)*(r+24)), ty=(float)(cy+Math.sin(a)*(r+24)); center(c,""+i,tx,ty+2,6.8f,MUTED,false); } }
            p.setStyle(Paint.Style.FILL); p.setColor(WHITE); c.drawCircle(X(cx),Y(cy),X(56),p); center(c,"16",cx,cy-3,32,TEXT,true); center(c,"AGO",cx,cy+19,8,MUTED,true); center(c,pct(now)+"% hoje",cx,cy+34,8,GREEN,true);
            card(c,18,340,372,560,18); text(c,"16 de agosto",30,367,12,TEXT,true); for(int i=0;i<mainCount();i++){ float y=400+i*31; check(c,38,y-4,done(now,i)); text(c,habits.get(i).name,60,y-8,10.5f,TEXT,true); text(c,habits.get(i).goal,60,y+6,7.5f,MUTED,false); hits.add(new Hit(X(22),Y(y-18),X(360),Y(y+17),3,i)); }
        }

        void myDay(Canvas c){ text(c,"‹",18,40,24,TEXT,false); hits.add(new Hit(X(0),Y(12),X(52),Y(55),8,0)); center(c,"Meu Dia",195,42,18,TEXT,true); text(c,"Hoje",24,78,20,TEXT,true); text(c,"Domingo, 16 de agosto",24,99,10,MUTED,false); text(c,doneMain(now)+" de "+mainCount()+" concluídos",286,78,9.5f,GREEN,true); card(c,18,122,372,470,18); for(int i=0;i<mainCount();i++){ float y=168+i*55; check(c,40,y-4,done(now,i)); text(c,habits.get(i).name,62,y-9,13,TEXT,true); text(c,habits.get(i).goal,62,y+8,8.5f,MUTED,false); hits.add(new Hit(X(20),Y(y-26),X(368),Y(y+26),3,i)); } }

        void calendarPage(Canvas c){ text(c,"‹",18,40,24,TEXT,false); hits.add(new Hit(X(0),Y(12),X(52),Y(55),8,0)); center(c,"Calendário",195,42,18,TEXT,true); center(c,monthName(shownMonth),195,78,11,TEXT,true); text(c,"‹",28,78,20,TEXT,false); text(c,"›",352,78,20,TEXT,false); hits.add(new Hit(X(18),Y(56),X(70),Y(95),12,-1)); hits.add(new Hit(X(320),Y(56),X(382),Y(95),12,1)); drawCalendarGrid(c,34,125,356,355,shownMonth,false); card(c,18,430,372,508,18); int mp=monthPct(shownMonth); text(c,mp<0?"-":mp+"%",32,474,23,GREEN,true); text(c,"Consistência do mês",92,462,10,TEXT,false); text(c,"Baseado nos registros reais do app",92,481,8,MUTED,false); }
        void insightsPage(Canvas c){ text(c,"‹",18,40,24,TEXT,false); hits.add(new Hit(X(0),Y(12),X(52),Y(55),8,0)); center(c,"Insights da Oliven",195,42,18,TEXT,true); String[][] a={{"↗","Você é mais consistente","nas segundas e terças.","Taxa média nesses dias: 87%"},{"◷","Suas noites após as 21h","têm menor conclusão.","Considere ajustar sua rotina."},{"↗","Seu desempenho geral","melhorou 8% este mês.","Continue evoluindo!"}}; for(int i=0;i<3;i++){ float t=92+i*126; card(c,18,t,372,t+100,18); text(c,a[i][0],36,t+54,14,GREEN,true); text(c,a[i][1],78,t+40,12,TEXT,true); text(c,a[i][2],78,t+58,12,TEXT,true); text(c,a[i][3],78,t+80,8,MUTED,false); } }
        void yearPage(Canvas c){ text(c,"‹",18,40,24,TEXT,false); hits.add(new Hit(X(0),Y(12),X(52),Y(55),8,0)); center(c,"Meu ano em 2026",195,42,18,TEXT,true); String[] mm={"JAN","FEV","MAR","ABR","MAI","JUN","JUL","AGO","SET","OUT","NOV","DEZ"}; for(int i=0;i<12;i++){ int row=i/4,col=i%4; float x=60+col*90,y=114+row*118; center(c,mm[i],x,y-24,8,MUTED,true); Calendar m=Calendar.getInstance(); m.set(Calendar.YEAR,2026); m.set(Calendar.MONTH,i); m.set(Calendar.DAY_OF_MONTH,1); int val=monthPct(m); p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(X(2.2f)); p.setColor(val<0?BORDER:GREEN); c.drawCircle(X(x),Y(y),X(27),p); center(c,val<0?"-":val+"%",x,y+5,9,val<0?MUTED:TEXT,true); } }

        void bottom(Canvas c){
            round(c,0,navTop,390,H,0,WHITE); line(c,0,navTop,390,navTop,BORDER,.7f); String[] labs={"Hoje","Progresso","Hábitos","Perfil"}; String[] icons={"⌂","↗","✓","♙"}; for(int i=0;i<4;i++){ float x=55+i*93; int col=(screen==i?GREEN:MUTED); center(c,icons[i],x,navTop+27,17,col,false); center(c,labs[i],x,navTop+50,9,col,screen==i); hits.add(new Hit(X(i*97),Y(navTop),X((i+1)*97),Y(H),2,i)); }
        }
        void drawer(Canvas c){
            p.setStyle(Paint.Style.FILL); p.setColor(0x66000000); c.drawRect(0,0,getWidth(),getHeight(),p); card(c,24,74,366,610,18); logo(c,52,104,38,true); String[] items={"Tela Inicial","Círculo","Evolução","Meu Dia","Hábitos","Calendário","Insights da Oliven","Meu Ano","Perfil"}; int[] screens={0,4,1,5,2,6,7,8,3}; for(int i=0;i<items.length;i++){ float y=170+i*43; text(c,items[i],56,y,14,TEXT,false); hits.add(new Hit(X(42),Y(y-26),X(350),Y(y+10),10,screens[i])); } }

        @Override public boolean onTouchEvent(android.view.MotionEvent e){ if(e.getAction()!=MotionEvent.ACTION_UP) return true; float x=e.getX(), y=e.getY();
            if(menu){ for(int i=hits.size()-1;i>=0;i--){ Hit h=hits.get(i); if(h.type==10 && h.r.contains(x,y)){ screen=h.index; menu=false; invalidate(); return true; } } menu=false; invalidate(); return true; }
            for(int i=hits.size()-1;i>=0;i--){ Hit h=hits.get(i); if(!h.r.contains(x,y)) continue; switch(h.type){
                case 1: menu=true; invalidate(); return true; case 2: screen=h.index; invalidate(); return true; case 3: toggle(h.index); invalidate(); return true; case 4: screen=4; invalidate(); return true; case 5: selectedPeriod=h.index; invalidate(); return true; case 6: selectedCat=h.index; invalidate(); return true; case 7: showAdd(); return true; case 8: screen=0; invalidate(); return true; case 9: shownMonth.add(Calendar.MONTH,h.index); invalidate(); return true; case 11: screen=7; invalidate(); return true; case 12: shownMonth.add(Calendar.MONTH,h.index); invalidate(); return true; }
            } return true;
        }
        void toggle(int index){ if(index<0||index>=habits.size())return; boolean v=done(now,index); prefs.edit().putBoolean(key(now,habits.get(index).id),!v).putBoolean(touched(now),true).apply(); }
        void showAdd(){
            final EditText nome=new EditText(getContext()); nome.setHint("Nome do hábito"); final EditText meta=new EditText(getContext()); meta.setHint("Meta"); LinearLayout box=new LinearLayout(getContext()); box.setOrientation(LinearLayout.VERTICAL); int pad=(int)X(20); box.setPadding(pad,0,pad,0); box.addView(nome); box.addView(meta);
            new AlertDialog.Builder(getContext()).setTitle("Novo hábito").setView(box).setNegativeButton("Cancelar",null).setPositiveButton("Adicionar",(d,w)->{ String n=nome.getText().toString().trim(), g=meta.getText().toString().trim(); if(n.isEmpty())return; int id=1; for(Habit h:habits) id=Math.max(id,h.id+1); habits.add(new Habit(id,n,g.isEmpty()?"Diário":g, selectedCat>0?cats[selectedCat]:"Pessoal")); saveHabits(); selectedCat=0; invalidate(); }).show();
        }
    }
}
