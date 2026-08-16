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

    static class Habit {
        int id; String name, goal, cat, icon;
        Habit(int id,String name,String goal,String cat,String icon){this.id=id;this.name=name;this.goal=goal;this.cat=cat;this.icon=icon;}
    }

    static class OlivenView extends View {
        final int BG=Color.rgb(250,251,248), WHITE=Color.WHITE, TEXT=Color.rgb(24,30,25), MUTED=Color.rgb(101,108,102), GREEN=Color.rgb(35,107,75), GREEN2=Color.rgb(82,150,79), SOFT=Color.rgb(239,245,236), BORDER=Color.rgb(224,229,222), LIGHT=Color.rgb(233,238,231), VERYLIGHT=Color.rgb(247,249,245);
        final Paint p=new Paint(Paint.ANTI_ALIAS_FLAG);
        final ArrayList<Habit> habits=new ArrayList<>();
        final ArrayList<RectF> rowHits=new ArrayList<>();
        final RectF menuHit=new RectF(), ringHit=new RectF(), todayCardHit=new RectF(), insightHit=new RectF(), plusHit=new RectF();
        final RectF[] bottomHits={new RectF(),new RectF(),new RectF(),new RectF()};
        SharedPreferences prefs;
        Calendar now=Calendar.getInstance();
        float s=1f,H=760,navTop=690;
        int screen=0; // 0 home,1 circle,2 evolution,3 myday,4 habits,5 calendar,6 insights,7 year,8 profile
        boolean drawer=false;
        final String[] drawerNames={"Tela Inicial","Círculo","Evolução","Meu Dia","Hábitos","Calendário","Insights da Oliven","Meu Ano","Perfil"};
        final int[] drawerScreens={0,1,2,3,4,5,6,7,8};
        final String[] months={"Janeiro","Fevereiro","Março","Abril","Maio","Junho","Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"};
        final String[] monthsShort={"JAN","FEV","MAR","ABR","MAI","JUN","JUL","AGO","SET","OUT","NOV","DEZ"};

        OlivenView(Context c){
            super(c); setLayerType(View.LAYER_TYPE_SOFTWARE,null);
            prefs=c.getSharedPreferences("oliven",Context.MODE_PRIVATE);
            habits.add(new Habit(1,"Academia","0 / 60 min","Corpo","⌁"));
            habits.add(new Habit(2,"Projeto Homem de Ferro","1h42 / 2h","Projetos","◆"));
            habits.add(new Habit(3,"Beber água","3,2 / 3 litros","Corpo","●"));
            habits.add(new Habit(4,"Leitura","0 / 30 min","Mente","▤"));
            habits.add(new Habit(5,"Organização","Concluída","Pessoal","✓"));
            habits.add(new Habit(6,"Cardio","4x por semana","Corpo","♥"));
            habits.add(new Habit(7,"Estudo","1h por dia","Mente","▤"));
        }

        float X(float v){return v*s;} float Y(float v){return v*s;}
        String todayDate(){return new SimpleDateFormat("yyyyMMdd",Locale.US).format(now.getTime());}
        String dateKey(Calendar c,int id){return "done_"+new SimpleDateFormat("yyyyMMdd",Locale.US).format(c.getTime())+"_"+id;}
        boolean isDone(Calendar c,int i){return prefs.getBoolean(dateKey(c,habits.get(i).id),false);}
        boolean isDoneToday(int i){return isDone(now,i);}
        int doneToday(){int n=0;for(int i=0;i<Math.min(5,habits.size());i++)if(isDoneToday(i))n++;return n;}
        int todayPct(){return doneToday()*20;}
        int dayPct(int day){Calendar c=(Calendar)now.clone();c.set(Calendar.DAY_OF_MONTH,day);int n=0;for(int i=0;i<5;i++)if(isDone(c,i))n++;return n*20;}
        int monthPct(){int d=now.get(Calendar.DAY_OF_MONTH);if(d<=0)return 0;int sum=0;for(int i=1;i<=d;i++)sum+=dayPct(i);return Math.round(sum/(float)d);}
        int pastActiveDays(){int d=now.get(Calendar.DAY_OF_MONTH),n=0;for(int i=1;i<=d;i++)if(dayPct(i)>0)n++;return n;}
        int consecutiveDays(){int d=now.get(Calendar.DAY_OF_MONTH),seq=0;for(int i=d;i>=1;i--){if(dayPct(i)>0)seq++;else break;}return seq;}

        void font(float z,int color,boolean bold){p.clearShadowLayer();p.setTypeface(Typeface.create("sans",bold?Typeface.BOLD:Typeface.NORMAL));p.setTextSize(X(z));p.setColor(color);p.setStyle(Paint.Style.FILL);}
        void text(Canvas c,String t,float x,float y,float z,int color,boolean bold){font(z,color,bold);p.setTextAlign(Paint.Align.LEFT);c.drawText(t,X(x),Y(y),p);}
        void center(Canvas c,String t,float x,float y,float z,int color,boolean bold){font(z,color,bold);p.setTextAlign(Paint.Align.CENTER);c.drawText(t,X(x),Y(y),p);p.setTextAlign(Paint.Align.LEFT);}
        void round(Canvas c,float l,float t,float r,float b,float rad,int color){p.clearShadowLayer();p.setStyle(Paint.Style.FILL);p.setColor(color);c.drawRoundRect(X(l),Y(t),X(r),Y(b),X(rad),X(rad),p);}
        void card(Canvas c,float l,float t,float r,float b,float rad){p.setStyle(Paint.Style.FILL);p.setColor(WHITE);p.setShadowLayer(X(1.4f),0,X(.9f),0x16000000);c.drawRoundRect(X(l),Y(t),X(r),Y(b),X(rad),X(rad),p);p.clearShadowLayer();p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(X(.65f));p.setColor(BORDER);c.drawRoundRect(X(l),Y(t),X(r),Y(b),X(rad),X(rad),p);}
        void line(Canvas c,float x1,float y1,float x2,float y2,int color,float w){p.clearShadowLayer();p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(X(w));p.setColor(color);c.drawLine(X(x1),Y(y1),X(x2),Y(y2),p);}
        void check(Canvas c,float x,float y,boolean done){p.clearShadowLayer();p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(X(1.2f));p.setColor(done?GREEN:MUTED);c.drawCircle(X(x),Y(y),X(5.4f),p);if(done){p.setStyle(Paint.Style.FILL);p.setColor(GREEN);c.drawCircle(X(x),Y(y),X(4.2f),p);font(5.6f,WHITE,true);p.setTextAlign(Paint.Align.CENTER);c.drawText("✓",X(x),Y(y+2),p);p.setTextAlign(Paint.Align.LEFT);}}
        int blend(int a,int b,float t){t=Math.max(0,Math.min(1,t));int ar=Color.red(a),ag=Color.green(a),ab=Color.blue(a);int br=Color.red(b),bg=Color.green(b),bb=Color.blue(b);return Color.rgb((int)(ar+(br-ar)*t),(int)(ag+(bg-ag)*t),(int)(ab+(bb-ab)*t));}
        int percentColor(int pct){if(pct<=0)return LIGHT;return blend(Color.rgb(221,238,217),GREEN,Math.max(.12f,pct/100f));}
        String monthName(){return months[now.get(Calendar.MONTH)]+" "+now.get(Calendar.YEAR);}
        String dateLabel(){return "Domingo, "+now.get(Calendar.DAY_OF_MONTH)+" de "+months[now.get(Calendar.MONTH)].toLowerCase(Locale.ROOT);}

        void hamburger(Canvas c,float x,float y){for(int i=0;i<3;i++)line(c,x,y+i*5.6f,x+15,y+i*5.6f,TEXT,1.2f);menuHit.set(X(x-10),Y(y-14),X(x+32),Y(y+28));}
        void back(Canvas c){text(c,"‹",17,37,23,TEXT,false);}
        void bell(Canvas c,float x,float y){p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(X(1.1f));p.setColor(TEXT);RectF r=new RectF(X(x-5),Y(y-7),X(x+5),Y(y+7));c.drawArc(r,205,130,false,p);line(c,x-6,y+4,x+6,y+4,TEXT,1.1f);}
        void topTitle(Canvas c,String title,boolean menu){if(menu)hamburger(c,21,25);else back(c);center(c,title,195,37,16.5f,TEXT,true);}

        void segmentedRing(Canvas c,float cx,float cy,float r,int value,float stroke){RectF rr=new RectF(X(cx-r),Y(cy-r),X(cx+r),Y(cy+r));p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(X(stroke));p.setStrokeCap(Paint.Cap.BUTT);int fill=Math.round(value*.6f);for(int i=0;i<60;i++){p.setColor(i<fill?GREEN2:LIGHT);c.drawArc(rr,-90+i*6,4.1f,false,p);}p.setStrokeCap(Paint.Cap.ROUND);}

        @Override protected void onDraw(Canvas c){
            super.onDraw(c); s=getWidth()/390f; H=getHeight()/s; navTop=H-63; c.drawColor(BG); rowHits.clear();
            switch(screen){
                case 0:home(c);break;case 1:circlePage(c);break;case 2:evolution(c);break;case 3:myDay(c);break;case 4:habitsPage(c);break;case 5:calendarPage(c);break;case 6:insightsPage(c);break;case 7:yearPage(c);break;default:profilePage(c);break;
            }
            if(screen!=1 && screen!=3 && screen!=5 && screen!=6 && screen!=7) bottom(c);
            if(drawer)drawer(c);
        }

        void brand(Canvas c){hamburger(c,21,25);p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(X(1.2f));p.setColor(GREEN);c.drawCircle(X(65),Y(30),X(10),p);line(c,59,30,71,30,GREEN,1.2f);p.setStyle(Paint.Style.FILL);p.setColor(GREEN);c.drawCircle(X(59),Y(30),X(2),p);c.drawCircle(X(71),Y(30),X(2),p);text(c,"Oliven",82,36,17,GREEN,true);bell(c,360,27);}

        void home(Canvas c){
            brand(c);text(c,"Bom dia, Jean",20,72,22,TEXT,true);text(c,dateLabel(),20,91,10,MUTED,false);
            float cy=206;segmentedRing(c,195,cy,86,monthPct(),7.1f);center(c,monthPct()+"%",195,cy+4,37,TEXT,true);center(c,"Consistência",195,cy+27,11,MUTED,false);center(c,"deste mês",195,cy+41,11,MUTED,false);String level=monthPct()>=80?"Excelente":monthPct()>=60?"Bom ritmo":"Construindo ritmo";round(c,159,cy+52,231,cy+72,10,SOFT);center(c,level,195,cy+66,8.8f,GREEN,true);ringHit.set(X(99),Y(cy-95),X(291),Y(cy+95));
            float top=322,bottom=Math.min(navTop-91,580);card(c,18,top,372,bottom,17);text(c,"HOJE",34,top+28,12,TEXT,true);text(c,doneToday()+" de 5 concluídos",274,top+28,10,GREEN,true);float row=(bottom-top-47)/5f;for(int i=0;i<5;i++){float yy=top+54+i*row;round(c,31,yy-15,59,yy+13,9,SOFT);center(c,habits.get(i).icon,45,yy+3,10,i==5?Color.RED:GREEN,true);text(c,habits.get(i).name,70,yy-3,11,TEXT,true);text(c,habits.get(i).goal,70,yy+11,8,MUTED,false);check(c,344,yy-2,isDoneToday(i));rowHits.add(new RectF(X(25),Y(yy-row/2),X(360),Y(yy+row/2)));}todayCardHit.set(X(18),Y(top),X(372),Y(bottom));
            float it=bottom+10;round(c,18,it,372,Math.min(navTop-12,it+55),16,SOFT);text(c,"↗",32,it+31,14,GREEN,true);text(c,"Você está "+Math.max(0,monthPct()-73)+"% acima do seu ritmo recente.",62,it+25,10,TEXT,true);text(c,"Toque para ver os insights da Oliven",62,it+40,8,MUTED,false);insightHit.set(X(18),Y(it),X(372),Y(it+55));
        }

        void circlePage(Canvas c){
            topTitle(c,"Círculo",false);text(c,"‹",23,73,18,TEXT,false);text(c,"›",356,73,18,TEXT,false);center(c,monthName(),195,72,11,TEXT,true);
            float cx=195,cy=213,r=89,total=29;int dim=now.getActualMaximum(Calendar.DAY_OF_MONTH);for(int d=1;d<=dim;d++){double a=Math.toRadians(-90+(d-1)*(360.0/dim));float x=(float)(cx+Math.cos(a)*r),y=(float)(cy+Math.sin(a)*r);int pct=dayPct(d);float prog=total*(pct/100f);c.save();c.rotate((float)Math.toDegrees(a)+90,X(x),Y(y));round(c,x-5.5f,y-total/2,x+5.5f,y+total/2,2.3f,LIGHT);if(prog>0)round(c,x-5.5f,y+total/2-prog,x+5.5f,y+total/2,2.3f,percentColor(pct));c.restore();if(d%2==1||d==now.get(Calendar.DAY_OF_MONTH)){float tx=(float)(cx+Math.cos(a)*(r+22)),ty=(float)(cy+Math.sin(a)*(r+22));center(c,""+d,tx,ty+2,6.5f,d==now.get(Calendar.DAY_OF_MONTH)?GREEN:MUTED,d==now.get(Calendar.DAY_OF_MONTH));}}
            p.setStyle(Paint.Style.FILL);p.setColor(WHITE);c.drawCircle(X(cx),Y(cy),X(52),p);center(c,""+now.get(Calendar.DAY_OF_MONTH),cx,cy-3,31,TEXT,true);center(c,monthsShort[now.get(Calendar.MONTH)],cx,cy+16,8,MUTED,true);center(c,"Hoje · "+todayPct()+"%",cx,cy+30,8,GREEN,true);
            float top=335,bottom=Math.min(navTop-18,565);card(c,18,top,372,bottom,16);text(c,now.get(Calendar.DAY_OF_MONTH)+" de "+months[now.get(Calendar.MONTH)].toLowerCase(Locale.ROOT),32,top+27,12,TEXT,true);float row=(bottom-top-40)/5f;for(int i=0;i<5;i++){float yy=top+54+i*row;check(c,40,yy-4,isDoneToday(i));text(c,habits.get(i).name,61,yy-6,10.5f,TEXT,true);text(c,habits.get(i).goal,61,yy+8,7.8f,MUTED,false);rowHits.add(new RectF(X(24),Y(yy-row/2),X(360),Y(yy+row/2)));}
        }

        void evolution(Canvas c){
            topTitle(c,"Evolução",true);String[] tabs={"7 dias","30 dias","90 dias","1 ano"};for(int i=0;i<4;i++){float l=18+i*89;round(c,l,49,l+84,77,15,i==1?SOFT:WHITE);center(c,tabs[i],l+42,67,8.3f,i==1?TEXT:MUTED,i==1);}
            card(c,18,90,372,293,16);text(c,"Taxa de consistência",31,116,10.5f,TEXT,true);text(c,monthPct()+"%",31,154,29,TEXT,true);text(c,"↑ "+Math.max(0,monthPct()-73)+"% vs período anterior",31,174,9,GREEN,true);for(int i=0;i<4;i++)line(c,55,205+i*21,352,205+i*21,BORDER,.55f);Path path=new Path();int days=Math.min(12,now.get(Calendar.DAY_OF_MONTH));for(int i=0;i<days;i++){int d=Math.max(1,now.get(Calendar.DAY_OF_MONTH)-days+1+i);float xx=55+i*(297f/Math.max(1,days-1));float yy=278-(dayPct(d)*.65f);if(i==0)path.moveTo(X(xx),Y(yy));else path.lineTo(X(xx),Y(yy));}p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(X(1.8f));p.setColor(GREEN);c.drawPath(path,p);
            card(c,18,307,372,442,16);text(c,"Resumo",31,333,12,TEXT,true);String[] rs={"Hoje","Semana","Mês","Últimos 90 dias"};int[] vals={todayPct(),Math.round((todayPct()+monthPct())/2f),monthPct(),monthPct()};for(int i=0;i<4;i++){text(c,rs[i],31,359+i*22,9.5f,TEXT,false);text(c,vals[i]+"%",338,359+i*22,9.5f,GREEN,true);}
            card(c,18,456,372,525,16);text(c,"Tendência",31,480,9,MUTED,false);text(c,"↑ "+Math.max(0,monthPct()-73)+"%",31,507,19,GREEN,true);text(c,"Melhor que o período anterior",115,507,8,MUTED,false);
        }

        void myDay(Canvas c){
            topTitle(c,"Meu Dia",false);text(c,"Hoje",22,82,18,TEXT,true);text(c,dateLabel(),22,101,9.5f,MUTED,false);text(c,doneToday()+" de 5 concluídos",285,82,9.5f,GREEN,true);float top=122,bottom=Math.min(navTop-105,535);card(c,18,top,372,bottom,16);float row=(bottom-top-20)/5f;for(int i=0;i<5;i++){float yy=top+39+i*row;check(c,40,yy-2,isDoneToday(i));text(c,habits.get(i).name,62,yy-4,12,TEXT,true);text(c,habits.get(i).goal,62,yy+12,8.5f,MUTED,false);rowHits.add(new RectF(X(24),Y(yy-row/2),X(360),Y(yy+row/2)));}float it=bottom+15;round(c,18,it,372,it+67,16,SOFT);text(c,"★",37,it+40,15,GREEN,true);text(c,"Pequenas ações, grandes resultados",70,it+30,10.5f,TEXT,true);text(c,"no final do dia.",70,it+46,10.5f,TEXT,true);
        }

        void habitsPage(Canvas c){
            topTitle(c,"Hábitos",true);plusHit.set(X(340),Y(15),X(378),Y(50));p.setStyle(Paint.Style.FILL);p.setColor(GREEN);c.drawCircle(X(355),Y(29),X(11),p);center(c,"+",355,34,17,WHITE,true);String[] cats={"Todos","Corpo","Mente","Projetos","Pessoal"};for(int i=0;i<5;i++){float l=18+i*70;round(c,l,55,l+66,82,14,i==0?SOFT:WHITE);center(c,cats[i],l+33,73,8,i==0?GREEN:MUTED,i==0);}
            float top=94,row=59;for(int i=0;i<7;i++){float t=top+i*row;card(c,18,t,372,t+51,15);round(c,30,t+9,67,t+42,11,SOFT);center(c,habits.get(i).icon,48.5f,t+31,10,i==5?Color.rgb(230,54,69):GREEN,true);text(c,habits.get(i).name,82,t+25,11,TEXT,true);text(c,habits.get(i).cat+" · "+habits.get(i).goal,82,t+39,7.8f,MUTED,false);text(c,"⋮",345,t+32,16,MUTED,false);}
        }

        void calendarPage(Canvas c){
            topTitle(c,"Calendário",false);text(c,"‹",25,72,18,TEXT,false);text(c,"›",355,72,18,TEXT,false);center(c,monthName(),195,71,11,TEXT,true);String[] wk={"D","S","T","Q","Q","S","S"};for(int i=0;i<7;i++)center(c,wk[i],50+i*48,111,7.5f,MUTED,true);
            Calendar first=(Calendar)now.clone();first.set(Calendar.DAY_OF_MONTH,1);int start=first.get(Calendar.DAY_OF_WEEK)-1;int dim=now.getActualMaximum(Calendar.DAY_OF_MONTH);int day=1;for(int cell=0;cell<42&&day<=dim;cell++){if(cell<start)continue;int row=(cell)/7,col=cell%7;float x=50+col*48,y=145+row*42;int pct=dayPct(day);if(day<=now.get(Calendar.DAY_OF_MONTH)){int colr=percentColor(pct);p.setStyle(Paint.Style.FILL);p.setColor(colr);c.drawCircle(X(x),Y(y-4),X(13),p);}center(c,""+day,x,y,8.5f,day==now.get(Calendar.DAY_OF_MONTH)?WHITE:(pct>=80?WHITE:MUTED),day==now.get(Calendar.DAY_OF_MONTH));day++;}
            float top=410;card(c,18,top,372,top+83,16);text(c,monthPct()+"%",31,top+48,24,GREEN,true);text(c,"Consistência do mês",92,top+34,10,TEXT,true);text(c,pastActiveDays()+" dias com registro",92,top+51,8.5f,MUTED,false);text(c,"A cor de cada dia representa o percentual atingido.",31,top+70,7.5f,MUTED,false);
        }

        void insightsPage(Canvas c){
            topTitle(c,"Insights da Oliven",false);float[] tops={75,185,295};String[] title1={"Você é mais consistente","Suas noites após as 21h","Seu desempenho geral"};String[] title2={"nas segundas e terças.","têm menor conclusão.","melhorou este mês."};String[] sub={"Taxa média nesses dias: 87%","Considere ajustar sua rotina.","Continue evoluindo!"};String[] ico={"↗","◷","↗"};for(int i=0;i<3;i++){card(c,18,tops[i],372,tops[i]+96,16);text(c,ico[i],34,tops[i]+48,14,GREEN,true);text(c,title1[i],70,tops[i]+35,11.2f,TEXT,true);text(c,title2[i],70,tops[i]+53,11.2f,TEXT,true);text(c,sub[i],70,tops[i]+74,8.5f,MUTED,false);}round(c,18,410,372,461,15,SOFT);text(c,"Ver todos os insights",31,441,10,TEXT,true);text(c,"›",345,442,18,MUTED,false);
        }

        void yearPage(Canvas c){
            topTitle(c,"Meu ano em "+now.get(Calendar.YEAR),false);text(c,"›",355,37,18,TEXT,false);int[] mock={92,81,76,88,73,84,79,82,-1,-1,-1,-1};for(int i=0;i<12;i++){int row=i/4,col=i%4;float x=56+col*92,y=100+row*111;center(c,monthsShort[i],x,y,8,MUTED,true);int v=i<now.get(Calendar.MONTH)?mock[i]:(i==now.get(Calendar.MONTH)?monthPct():-1);p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(X(1.7f));p.setColor(v>=0?GREEN:BORDER);c.drawCircle(X(x),Y(y+33),X(25),p);center(c,v>=0?v+"%":"–",x,y+37,9,TEXT,true);}
        }

        void profilePage(Canvas c){
            topTitle(c,"Perfil",true);card(c,18,55,372,124,16);p.setStyle(Paint.Style.FILL);p.setColor(GREEN);c.drawCircle(X(55),Y(89),X(23),p);center(c,"J",55,96,19,WHITE,true);text(c,"Jean Silva",93,87,12.5f,TEXT,true);text(c,"Membro desde abr/2024",93,103,8,MUTED,false);String[][] rows={{"Dados pessoais","Nome, preferências e objetivo"},{"Preferências","Aparência e rotina"},{"Notificações","Lembretes da rotina"},{"Backup e sincronização","Em breve"},{"Ajuda e suporte","Central de ajuda"},{"Sobre a Oliven","Oliven 1.0.8 · Android nativo"}};float t=136;for(String[] r:rows){card(c,18,t,372,t+48,14);text(c,r[0],31,t+22,10.5f,TEXT,true);text(c,r[1],31,t+36,7.8f,MUTED,false);text(c,"›",344,t+32,17,MUTED,false);t+=55;}
        }

        void bottom(Canvas c){
            round(c,0,navTop,390,H,0,WHITE);line(c,0,navTop,390,navTop,BORDER,.55f);String[] labels={"Hoje","Progresso","Hábitos","Perfil"};String[] icons={"⌂","↗","✓","♙"};int[] map={0,2,4,8};float[] xs={54,152,241,335};for(int i=0;i<4;i++){boolean active=screen==map[i];center(c,icons[i],xs[i],navTop+23,14,active?GREEN:MUTED,active);center(c,labels[i],xs[i],navTop+43,8.5f,active?GREEN:MUTED,active);bottomHits[i].set(X(xs[i]-42),Y(navTop),X(xs[i]+42),Y(H));}}

        void drawer(Canvas c){
            p.setStyle(Paint.Style.FILL);p.setColor(0x88000000);c.drawRect(X(300),0,X(390),Y(H),p);round(c,0,0,302,H,0,WHITE);p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(X(1.2f));p.setColor(GREEN);c.drawCircle(X(44),Y(39),X(11),p);line(c,38,39,50,39,GREEN,1.2f);text(c,"Oliven",64,45,18,TEXT,true);float y=77;for(int i=0;i<drawerNames.length;i++){if(screen==drawerScreens[i])round(c,18,y-20,282,y+12,13,SOFT);text(c,i==0?"⌂":i==1?"◷":i==2?"↗":i==3?"✓":i==4?"✣":i==5?"▣":i==6?"◷":i==7?"▧":"♙",36,y,11,screen==drawerScreens[i]?GREEN:MUTED,true);text(c,drawerNames[i],70,y,10,screen==drawerScreens[i]?GREEN:TEXT,screen==drawerScreens[i]);y+=39;}round(c,18,H-78,282,H-22,14,SOFT);text(c,"Oliven",35,H-51,11,GREEN,true);text(c,"Evolua todos os dias.",83,H-53,9,TEXT,true);text(c,"O progresso é construído nos detalhes.",83,H-38,7.5f,MUTED,false);
        }

        void toggleHabit(int index){if(index<0||index>=5)return;String k=dateKey(now,habits.get(index).id);prefs.edit().putBoolean(k,!prefs.getBoolean(k,false)).apply();invalidate();}
        @Override public boolean onTouchEvent(android.view.MotionEvent e){if(e.getAction()!=MotionEvent.ACTION_UP)return true;float x=e.getX(),y=e.getY();
            if(drawer){if(x>X(302)){drawer=false;invalidate();return true;}float yy=Y(77);for(int i=0;i<drawerNames.length;i++){if(y>=yy-Y(22)&&y<=yy+Y(15)){screen=drawerScreens[i];drawer=false;invalidate();return true;}yy+=Y(39);}return true;}
            if(menuHit.contains(x,y)){drawer=true;invalidate();return true;}
            for(int i=0;i<4;i++)if(bottomHits[i].contains(x,y)){screen=new int[]{0,2,4,8}[i];invalidate();return true;}
            if(screen==0){if(ringHit.contains(x,y)){screen=1;invalidate();return true;}if(insightHit.contains(x,y)){screen=6;invalidate();return true;}for(int i=0;i<Math.min(5,rowHits.size());i++)if(rowHits.get(i).contains(x,y)){toggleHabit(i);return true;}if(todayCardHit.contains(x,y)){screen=3;invalidate();return true;}}
            if(screen==1||screen==3){for(int i=0;i<Math.min(5,rowHits.size());i++)if(rowHits.get(i).contains(x,y)){toggleHabit(i);return true;}if(x<X(55)&&y<Y(65)){screen=0;invalidate();return true;}}
            if((screen==5||screen==6||screen==7)&&x<X(55)&&y<Y(65)){screen=2;invalidate();return true;}
            return true;}
    }
}
