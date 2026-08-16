package com.oliven.app;

import android.app.Activity;
import android.os.Bundle;
import android.content.Context;
import android.content.SharedPreferences;
import android.graphics.*;
import android.view.*;
import java.text.SimpleDateFormat;
import java.util.*;

public class MainActivity extends Activity {
    @Override public void onCreate(Bundle b){
        super.onCreate(b);
        getWindow().setStatusBarColor(Color.rgb(250,251,248));
        getWindow().setNavigationBarColor(Color.WHITE);
        getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR|View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR);
        setContentView(new OlivenView(this));
    }

    static class Habit { int id; String name, goal, cat; Habit(int id,String n,String g,String c){this.id=id;name=n;goal=g;cat=c;} }

    static class OlivenView extends View {
        final int BG=Color.rgb(250,251,248), WHITE=Color.WHITE, TEXT=Color.rgb(26,32,27), MUTED=Color.rgb(104,111,105), GREEN=Color.rgb(35,107,75), GREEN2=Color.rgb(84,160,92), SOFT=Color.rgb(239,245,236), BORDER=Color.rgb(226,230,223), LIGHT=Color.rgb(233,238,231), OLIVE=Color.rgb(116,138,53);
        final Paint p=new Paint(Paint.ANTI_ALIAS_FLAG);
        final ArrayList<Habit> habits=new ArrayList<>();
        final ArrayList<RectF> habitHits=new ArrayList<>();
        final RectF menuHit=new RectF(), ringHit=new RectF(), insightHit=new RectF();
        SharedPreferences prefs;
        Calendar now=Calendar.getInstance();
        float s=1f,H=760,navTop=690;
        int screen=0;
        boolean menu=false;
        final String[] menuNames={"Tela Inicial","Círculo","Evolução","Meu Dia","Hábitos","Calendário","Insights da Oliven","Meu Ano","Perfil"};

        OlivenView(Context c){
            super(c); setLayerType(View.LAYER_TYPE_SOFTWARE,null);
            prefs=c.getSharedPreferences("oliven",Context.MODE_PRIVATE);
            habits.add(new Habit(1,"Academia","5x por semana","Corpo"));
            habits.add(new Habit(2,"Projeto Homem de Ferro","1h42 / 2h","Projetos"));
            habits.add(new Habit(3,"Beber água","3,2 / 3 litros","Corpo"));
            habits.add(new Habit(4,"Leitura","30 min por dia","Mente"));
            habits.add(new Habit(5,"Organização","Diário","Pessoal"));
            habits.add(new Habit(6,"Cardio","4x por semana","Corpo"));
            habits.add(new Habit(7,"Estudo","1h por dia","Mente"));
        }

        float X(float v){return v*s;} float Y(float v){return v*s;}
        String key(int id){return "done_"+new SimpleDateFormat("yyyyMMdd",Locale.US).format(now.getTime())+"_"+id;}
        boolean isDone(int i){return prefs.getBoolean(key(habits.get(i).id),false);}
        int done(){int n=0;for(int i=0;i<Math.min(5,habits.size());i++)if(isDone(i))n++;return n;}
        int pct(){return done()*20;}
        int monthPct(){return Math.max(0,Math.min(100,(pct()+68)/17));}

        void font(float z,int color,boolean bold){p.setTypeface(Typeface.create("sans",bold?Typeface.BOLD:Typeface.NORMAL));p.setTextSize(X(z));p.setColor(color);p.setStyle(Paint.Style.FILL);p.setStrokeWidth(1);}
        void text(Canvas c,String t,float x,float y,float z,int color,boolean bold){font(z,color,bold);p.setTextAlign(Paint.Align.LEFT);c.drawText(t,X(x),Y(y),p);}
        void center(Canvas c,String t,float x,float y,float z,int color,boolean bold){font(z,color,bold);p.setTextAlign(Paint.Align.CENTER);c.drawText(t,X(x),Y(y),p);p.setTextAlign(Paint.Align.LEFT);}
        void round(Canvas c,float l,float t,float r,float b,float rad,int color){p.setStyle(Paint.Style.FILL);p.setColor(color);p.clearShadowLayer();c.drawRoundRect(X(l),Y(t),X(r),Y(b),X(rad),X(rad),p);}
        void card(Canvas c,float l,float t,float r,float b,float rad){p.setStyle(Paint.Style.FILL);p.setColor(WHITE);p.setShadowLayer(X(1.4f),0,X(.8f),0x13000000);c.drawRoundRect(X(l),Y(t),X(r),Y(b),X(rad),X(rad),p);p.clearShadowLayer();p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(X(.7f));p.setColor(BORDER);c.drawRoundRect(X(l),Y(t),X(r),Y(b),X(rad),X(rad),p);}
        void line(Canvas c,float x1,float y1,float x2,float y2,int color,float w){p.clearShadowLayer();p.setColor(color);p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(X(w));c.drawLine(X(x1),Y(y1),X(x2),Y(y2),p);}
        void circleStroke(Canvas c,float cx,float cy,float r,int color,float w){p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(X(w));p.setColor(color);c.drawCircle(X(cx),Y(cy),X(r),p);}

        @Override protected void onDraw(Canvas c){
            super.onDraw(c); s=getWidth()/390f; H=getHeight()/s; navTop=H-63f; c.drawColor(BG); habitHits.clear();
            switch(screen){case 0:home(c);break;case 1:evolution(c);break;case 2:habits(c);break;case 3:profile(c);break;case 4:circlePage(c);break;case 5:myDay(c);break;case 6:calendarPage(c);break;case 7:insights(c);break;case 8:year(c);break;}
            bottom(c); if(menu)drawer(c);
        }

        void hamburger(Canvas c,float x,float y){for(int i=0;i<3;i++)line(c,x,y+i*6,x+15,y+i*6,TEXT,1.25f);menuHit.set(X(x-10),Y(y-14),X(x+32),Y(y+30));}
        void bell(Canvas c,float x,float y){p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(X(1.1f));p.setColor(TEXT);RectF r=new RectF(X(x-5),Y(y-7),X(x+5),Y(y+7));c.drawArc(r,205,130,false,p);line(c,x-6,y+4,x+6,y+4,TEXT,1.1f);line(c,x,y+5,x,y+8,TEXT,1.1f);}
        void back(Canvas c){text(c,"‹",18,37,23,TEXT,false);}
        String date(){return "Domingo, 16 de agosto";}

        void segmentedRing(Canvas c,float cx,float cy,float r,int progress){
            RectF rr=new RectF(X(cx-r),Y(cy-r),X(cx+r),Y(cy+r));p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(X(5.5f));p.setStrokeCap(Paint.Cap.BUTT);int fill=Math.round(progress*.6f);
            for(int i=0;i<60;i++){p.setColor(i<fill?GREEN2:LIGHT);c.drawArc(rr,-90+i*6,4,false,p);}p.setStrokeCap(Paint.Cap.ROUND);
        }
        void check(Canvas c,float x,float y,boolean done){circleStroke(c,x,y,5,done?GREEN:MUTED,1);if(done){p.setStyle(Paint.Style.FILL);p.setColor(GREEN);c.drawCircle(X(x),Y(y),X(3.8f),p);}}

        void home(Canvas c){
            hamburger(c,23,24);bell(c,358,25);
            text(c,"Bom dia, Jean",20,65,20,TEXT,true); text(c,date(),20,82,10,MUTED,false);
            float cy=190; segmentedRing(c,195,cy,70,pct()); center(c,pct()+"%",195,cy+5,31,TEXT,true); center(c,"Consistência deste mês",195,cy+25,9,MUTED,false); ringHit.set(X(116),Y(cy-82),X(274),Y(cy+82));
            float cardTop=292,cardBottom=Math.min(navTop-120,552); card(c,18,cardTop,372,cardBottom,17); text(c,"HOJE",30,cardTop+26,11,TEXT,true); text(c,done()+" de 5 concluídos",286,cardTop+26,10,GREEN,true);
            float row=(cardBottom-cardTop-43)/5f; for(int i=0;i<5;i++){float yy=cardTop+48+i*row;check(c,39,yy-4,isDone(i));text(c,habits.get(i).name,55,yy-7,11,TEXT,true);text(c,habits.get(i).goal,55,yy+6,8,MUTED,false);habitHits.add(new RectF(X(24),Y(yy-row/2),X(360),Y(yy+row/2)));}
            float insightTop=cardBottom+10, insightBottom=Math.min(navTop-14,insightTop+56);round(c,18,insightTop,372,insightBottom,16,SOFT);text(c,"↗",31,insightTop+32,14,GREEN,true);text(c,"Seu ritmo está ficando mais consistente",56,insightTop+25,11,TEXT,true);text(c,"Toque para ver os insights da Oliven",56,insightTop+40,8,MUTED,false);insightHit.set(X(18),Y(insightTop),X(372),Y(insightBottom));
        }

        void topCentered(Canvas c,String title){hamburger(c,23,24);center(c,title,195,35,17,TEXT,true);}
        void evolution(Canvas c){
            topCentered(c,"Evolução");String[] chips={"7 dias","30 dias","90 dias","1 ano"};for(int i=0;i<4;i++){float l=18+i*89;round(c,l,48,l+84,76,15,i==1?SOFT:WHITE);center(c,chips[i],l+42,67,8.5f,i==1?TEXT:MUTED,i==1);}
            card(c,18,88,372,286,16);text(c,"Taxa de consistência",30,111,10,MUTED,false);text(c,monthPct()+"%",30,145,27,TEXT,true);text(c,"↑ 8% vs período anterior",30,163,9,GREEN,false);
            for(int i=0;i<3;i++)line(c,30,193+i*27,358,193+i*27,BORDER,.6f);float[] ys={253,238,224,208,216,201,206,187,191,173};Path path=new Path();for(int i=0;i<ys.length;i++){float xx=30+i*36.3f;if(i==0)path.moveTo(X(xx),Y(ys[i]));else path.lineTo(X(xx),Y(ys[i]));}p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(X(1.8f));p.setColor(GREEN);c.drawPath(path,p);
            card(c,18,299,372,449,16);text(c,"Resumo",30,323,12,TEXT,true);String[] a={"Hoje","Semana","Mês","Últimos 90 dias"};int[] v={pct(),Math.max(0,pct()/2),monthPct(),Math.max(0,monthPct()-6)};for(int i=0;i<4;i++){text(c,a[i],30,348+i*27,9.5f,TEXT,false);text(c,v[i]+"%",341,348+i*27,9.5f,GREEN,true);}card(c,18,463,372,535,16);text(c,"Tendência",30,484,9,MUTED,false);text(c,"↑ 8%",30,510,20,GREEN,true);text(c,"Melhor que o mês anterior",30,525,8,MUTED,false);
        }

        void habits(Canvas c){
            text(c,"Hábitos",18,46,24,TEXT,true);text(c,"Meus hábitos",18,64,9,MUTED,false);text(c,"+",349,47,22,TEXT,true);
            String[] cats={"Todos","Corpo","Mente","Projetos","Pessoal"};for(int i=0;i<5;i++){float l=18+i*70;round(c,l,74,l+66,100,14,i==0?SOFT:WHITE);center(c,cats[i],l+33,92,8,i==0?GREEN:MUTED,i==0);}
            String[] ic={"◉","◆","●","▤","✓","♥","▤"};float rowH=57;for(int i=0;i<7;i++){float t=112+i*rowH;card(c,18,t,372,t+50,15);round(c,30,t+8,65,t+42,11,SOFT);center(c,ic[i],47.5f,t+30,11,i==5?Color.rgb(230,54,69):GREEN,true);text(c,habits.get(i).name,77,t+24,11,TEXT,true);text(c,habits.get(i).goal,77,t+38,8,MUTED,false);text(c,"⋮",344,t+31,16,MUTED,false);}
        }

        void profile(Canvas c){
            topCentered(c,"Perfil");card(c,18,48,372,112,16);p.setStyle(Paint.Style.FILL);p.setColor(GREEN);c.drawCircle(X(55),Y(80),X(22),p);center(c,"J",55,87,19,WHITE,true);text(c,"Jean Silva",92,78,12,TEXT,true);text(c,"Membro desde abr/2024",92,92,8,MUTED,false);
            String[][] rows={{"Dados pessoais","Nome, preferências e objetivo"},{"Preferências","Aparência e rotina"},{"Notificações","Lembretes da rotina"},{"Backup e sincronização","Em breve"},{"Ajuda e suporte","Central de ajuda"},{"Sobre a Oliven","Oliven 1.0.6 · Android nativo"}};float t=122;for(int i=0;i<rows.length;i++){card(c,18,t,372,t+48,14);text(c,rows[i][0],30,t+22,10.5f,TEXT,true);text(c,rows[i][1],30,t+35,7.8f,MUTED,false);text(c,"›",344,t+31,17,MUTED,false);t+=56;}
        }

        void circlePage(Canvas c){
            back(c);center(c,"Círculo",195,37,16,TEXT,true);text(c,"▣",350,37,13,TEXT,false);text(c,"‹",25,68,18,TEXT,false);center(c,"Agosto 2026",195,67,10.5f,TEXT,true);text(c,"›",355,68,18,TEXT,false);
            float cx=195,cy=196,r=83;for(int i=0;i<31;i++){double a=Math.toRadians(-90+i*(360.0/31));float x=(float)(cx+Math.cos(a)*r),y=(float)(cy+Math.sin(a)*r);p.setColor(i<16?Color.rgb(126,194,113):LIGHT);p.setStyle(Paint.Style.FILL);c.save();c.rotate((float)Math.toDegrees(a)+90,X(x),Y(y));c.drawRoundRect(X(x-5),Y(y-10),X(x+5),Y(y+10),X(2),X(2),p);c.restore();if(i%2==0){float tx=(float)(cx+Math.cos(a)*(r+18)),ty=(float)(cy+Math.sin(a)*(r+18));center(c,String.valueOf(i+1),tx,ty+2,6.8f,MUTED,false);}}
            p.setColor(WHITE);p.setStyle(Paint.Style.FILL);c.drawCircle(X(cx),Y(cy),X(50),p);center(c,"16",cx,cy-2,28,TEXT,true);center(c,"AGO",cx,cy+15,7.5f,MUTED,true);center(c,"Domingo",cx,cy+28,8,TEXT,false);
            card(c,18,306,372,514,15);text(c,"16 de agosto",30,330,11,TEXT,true);for(int i=0;i<5;i++){float yy=361+i*29;check(c,36,yy-4,isDone(i));text(c,habits.get(i).name,56,yy,10,TEXT,true);text(c,habits.get(i).goal,56,yy+11,7.8f,MUTED,false);habitHits.add(new RectF(X(24),Y(yy-17),X(360),Y(yy+15)));}
        }

        void myDay(Canvas c){
            back(c);center(c,"Meu Dia",195,37,16,TEXT,true);text(c,"Hoje",24,70,18,TEXT,true);text(c,date(),24,87,9,MUTED,false);text(c,done()+" de 5 concluídos",288,70,9,GREEN,true);card(c,18,106,372,414,16);float row=56;for(int i=0;i<5;i++){float yy=143+i*row;check(c,38,yy,isDone(i));text(c,habits.get(i).name,58,yy-4,12,TEXT,true);text(c,habits.get(i).goal,58,yy+11,8,MUTED,false);habitHits.add(new RectF(X(24),Y(yy-25),X(360),Y(yy+25)));}
        }

        void calendarPage(Canvas c){
            back(c);center(c,"Calendário",195,37,16,TEXT,true);text(c,"‹",28,69,18,TEXT,false);center(c,"Agosto 2026",195,68,10,TEXT,true);text(c,"›",350,69,18,TEXT,false);String[] wk={"D","S","T","Q","Q","S","S"};for(int i=0;i<7;i++)center(c,wk[i],52+i*48,103,8,MUTED,false);int d=1;for(int row=0;row<6;row++)for(int col=0;col<7;col++){if(row==0&&col<6)continue;if(d>31)continue;float x=52+col*48,y=132+row*42;if(d==16){round(c,x-14,y-16,x+14,y+12,14,SOFT);center(c,"16",x,y+1,9,GREEN,true);}else{center(c,String.valueOf(d),x,y+1,9,MUTED,false);}d++;}
            card(c,18,405,372,474,15);text(c,"81%",30,438,22,GREEN,true);text(c,"Consistência do mês",86,434,9,TEXT,false);text(c,"25 dias concluídos",86,449,8,MUTED,false);
        }

        void insights(Canvas c){
            back(c);center(c,"Insights da Oliven",195,37,16,TEXT,true);String[][] rows={{"↗","Você é mais consistente","nas segundas e terças.","Taxa média nesses dias: 87%"},{"◷","Suas noites após as 21h","têm menor conclusão.","Considere ajustar sua rotina."},{"↗","Seu desempenho geral","melhorou 8% este mês.","Continue evoluindo!"}};float t=72;for(int i=0;i<3;i++){card(c,18,t,372,t+105,16);text(c,rows[i][0],35,t+40,14,GREEN,true);text(c,rows[i][1],70,t+31,11,TEXT,true);text(c,rows[i][2],70,t+47,11,TEXT,true);text(c,rows[i][3],70,t+69,8,MUTED,false);t+=119;}card(c,18,438,372,486,15);text(c,"Ver todos os insights",30,468,9.5f,TEXT,false);text(c,"›",344,468,16,MUTED,false);
        }

        void year(Canvas c){
            back(c);center(c,"Meu ano em 2026",195,37,16,TEXT,true);text(c,"›",350,37,18,TEXT,false);String[] m={"JAN","FEV","MAR","ABR","MAI","JUN","JUL","AGO","SET","OUT","NOV","DEZ"};String[] v={"92%","81%","76%","88%","73%","84%","79%","82%","–","–","–","–"};for(int i=0;i<12;i++){int col=i%4,row=i/4;float x=58+col*91,y=112+row*104;center(c,m[i],x,y-28,8,MUTED,true);circleStroke(c,x,y,24,i<8?GREEN:BORDER,2);center(c,v[i],x,y+4,9,i<8?TEXT:MUTED,true);}
        }

        void bottom(Canvas c){
            round(c,0,navTop,390,H,0,WHITE);line(c,0,navTop,390,navTop,BORDER,.6f);String[] labs={"Hoje","Progresso","Hábitos","Perfil"};String[] icons={"⌂","↗","✓","♙"};int[] target={0,1,2,3};for(int i=0;i<4;i++){float x=55+i*93;boolean on=screen==target[i]||(i==0&&(screen==4||screen==5||screen==6||screen==7||screen==8));center(c,icons[i],x,navTop+25,14,on?GREEN:MUTED,i==2);center(c,labs[i],x,navTop+45,8.5f,on?GREEN:MUTED,on);}
        }

        void drawer(Canvas c){
            p.setColor(0x88000000);p.setStyle(Paint.Style.FILL);c.drawRect(0,0,getWidth(),getHeight(),p);float l=24,t=54,r=366,b=Math.min(navTop-10,604);round(c,l,t,r,b,16,WHITE);text(c,"Oliven",46,89,18,TEXT,true);for(int i=0;i<menuNames.length;i++){float y=126+i*43;text(c,menuNames[i],46,y,13,TEXT,false);if(i<menuNames.length-1)line(c,46,y+15,344,y+15,Color.rgb(242,244,240),.5f);}}

        @Override public boolean onTouchEvent(android.view.MotionEvent e){if(e.getAction()!=MotionEvent.ACTION_UP)return true;float x=e.getX(),y=e.getY();
            if(menu){float sy=y/s;if(x<X(24)||x>X(366)||sy<54||sy>604){menu=false;invalidate();return true;}int idx=(int)((sy-105)/43);if(idx>=0&&idx<9){screen=new int[]{0,4,1,5,2,6,7,8,3}[idx];menu=false;invalidate();return true;}menu=false;invalidate();return true;}
            if(menuHit.contains(x,y)){menu=true;invalidate();return true;}
            if(screen==0&&ringHit.contains(x,y)){screen=4;invalidate();return true;}
            if(screen==0&&insightHit.contains(x,y)){screen=7;invalidate();return true;}
            for(int i=0;i<habitHits.size()&&i<5;i++)if(habitHits.get(i).contains(x,y)){prefs.edit().putBoolean(key(habits.get(i).id),!isDone(i)).apply();invalidate();return true;}
            float sy=y/s;if(sy>navTop){if(x<getWidth()*.25f)screen=0;else if(x<getWidth()*.5f)screen=1;else if(x<getWidth()*.75f)screen=2;else screen=3;invalidate();return true;}
            if((screen==4||screen==5||screen==6||screen==7||screen==8)&&x<X(75)&&sy<70){screen=0;invalidate();return true;}
            return true;}
    }
}
