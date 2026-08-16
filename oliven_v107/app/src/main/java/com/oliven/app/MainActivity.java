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

  static class Habit { int id; String name,goal,cat; Habit(int i,String n,String g,String c){id=i;name=n;goal=g;cat=c;} }

  static class OlivenView extends View {
    final int BG=Color.rgb(250,251,248), WHITE=Color.WHITE, TEXT=Color.rgb(25,31,26), MUTED=Color.rgb(104,111,105), GREEN=Color.rgb(35,107,75), GREEN2=Color.rgb(91,166,93), SOFT=Color.rgb(239,245,236), BORDER=Color.rgb(226,230,223), LIGHT=Color.rgb(233,238,231);
    final Paint p=new Paint(Paint.ANTI_ALIAS_FLAG); final ArrayList<Habit> habits=new ArrayList<>(); final ArrayList<RectF> hits=new ArrayList<>();
    SharedPreferences prefs; Calendar now=Calendar.getInstance(); float s=1f,H=760,navTop=690; int screen=0; boolean menu=false; RectF ringHit=new RectF(), todayHit=new RectF(), insightHit=new RectF(), menuHit=new RectF();

    OlivenView(Context c){ super(c); setLayerType(View.LAYER_TYPE_SOFTWARE,null); prefs=c.getSharedPreferences("oliven",Context.MODE_PRIVATE);
      habits.add(new Habit(1,"Academia","5x por semana","Corpo")); habits.add(new Habit(2,"Projeto Homem de Ferro","1h42 / 2h","Projetos")); habits.add(new Habit(3,"Beber água","3,2 / 3 litros","Corpo")); habits.add(new Habit(4,"Leitura","30 min por dia","Mente")); habits.add(new Habit(5,"Organização","Diário","Pessoal")); habits.add(new Habit(6,"Cardio","4x por semana","Corpo")); habits.add(new Habit(7,"Estudo","1h por dia","Mente")); }
    float X(float v){return v*s;} float Y(float v){return v*s;}
    String dateKey(int day,int id){ Calendar c=(Calendar)now.clone(); c.set(Calendar.DAY_OF_MONTH,day); return "done_"+new SimpleDateFormat("yyyyMMdd",Locale.US).format(c.getTime())+"_"+id; }
    boolean isDoneToday(int i){ return prefs.getBoolean(dateKey(now.get(Calendar.DAY_OF_MONTH),habits.get(i).id),false); }
    int dayPct(int day){ int d=0; for(int i=0;i<5;i++) if(prefs.getBoolean(dateKey(day,habits.get(i).id),false))d++; return d*20; }
    int done(){int d=0;for(int i=0;i<5;i++)if(isDoneToday(i))d++;return d;} int pct(){return done()*20;}
    int monthPct(){int day=now.get(Calendar.DAY_OF_MONTH),sum=0;for(int i=1;i<=day;i++)sum+=dayPct(i);return day==0?0:Math.round(sum/(float)day);}
    void font(float z,int col,boolean bold){p.setTypeface(Typeface.create("sans",bold?Typeface.BOLD:Typeface.NORMAL));p.setTextSize(X(z));p.setColor(col);p.setStyle(Paint.Style.FILL);p.clearShadowLayer();}
    void text(Canvas c,String t,float x,float y,float z,int col,boolean b){font(z,col,b);p.setTextAlign(Paint.Align.LEFT);c.drawText(t,X(x),Y(y),p);} void center(Canvas c,String t,float x,float y,float z,int col,boolean b){font(z,col,b);p.setTextAlign(Paint.Align.CENTER);c.drawText(t,X(x),Y(y),p);p.setTextAlign(Paint.Align.LEFT);}
    void round(Canvas c,float l,float t,float r,float b,float rad,int col){p.setStyle(Paint.Style.FILL);p.setColor(col);p.clearShadowLayer();c.drawRoundRect(X(l),Y(t),X(r),Y(b),X(rad),X(rad),p);} void card(Canvas c,float l,float t,float r,float b,float rad){p.setStyle(Paint.Style.FILL);p.setColor(WHITE);p.setShadowLayer(X(1.2f),0,X(.8f),0x12000000);c.drawRoundRect(X(l),Y(t),X(r),Y(b),X(rad),X(rad),p);p.clearShadowLayer();p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(X(.7f));p.setColor(BORDER);c.drawRoundRect(X(l),Y(t),X(r),Y(b),X(rad),X(rad),p);} void line(Canvas c,float x1,float y1,float x2,float y2,int col,float w){p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(X(w));p.setColor(col);c.drawLine(X(x1),Y(y1),X(x2),Y(y2),p);}
    void check(Canvas c,float x,float y,boolean d){p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(X(1));p.setColor(d?GREEN:MUTED);c.drawCircle(X(x),Y(y),X(5),p);if(d){p.setStyle(Paint.Style.FILL);p.setColor(GREEN);c.drawCircle(X(x),Y(y),X(3.8f),p);}}
    void hamburger(Canvas c,float x,float y){for(int i=0;i<3;i++)line(c,x,y+i*6,x+15,y+i*6,TEXT,1.2f);menuHit.set(X(x-10),Y(y-14),X(x+32),Y(y+30));}
    void bigRing(Canvas c,float cx,float cy,float r,int value){RectF rr=new RectF(X(cx-r),Y(cy-r),X(cx+r),Y(cy+r));p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(X(6.5f));p.setStrokeCap(Paint.Cap.BUTT);int fill=Math.round(value*.6f);for(int i=0;i<60;i++){p.setColor(i<fill?GREEN2:LIGHT);c.drawArc(rr,-90+i*6,4,false,p);}p.setStrokeCap(Paint.Cap.ROUND);}

    @Override protected void onDraw(Canvas c){super.onDraw(c);s=getWidth()/390f;H=getHeight()/s;navTop=H-63;c.drawColor(BG);hits.clear();if(screen==0)home(c);else if(screen==1)progress(c);else if(screen==2)habitPage(c);else if(screen==3)profile(c);else if(screen==4)circlePage(c);else myDay(c);bottom(c);if(menu)drawer(c);}

    void home(Canvas c){ hamburger(c,22,24);text(c,"Bom dia, Jean",20,62,20,TEXT,true);text(c,"Domingo, 16 de agosto",20,79,10,MUTED,false);
      float cy=188; bigRing(c,195,cy,86,pct());center(c,pct()+"%",195,cy+7,35,TEXT,true);center(c,"Consistência de hoje",195,cy+28,9,MUTED,false);ringHit.set(X(101),Y(cy-94),X(289),Y(cy+94));
      float top=300,bottom=Math.min(navTop-112,536);card(c,18,top,372,bottom,17);text(c,"HOJE",30,top+26,11,TEXT,true);text(c,done()+" de 5 concluídos",287,top+26,10,GREEN,true);float row=(bottom-top-42)/5f;for(int i=0;i<5;i++){float yy=top+48+i*row;check(c,39,yy-4,isDoneToday(i));text(c,habits.get(i).name,55,yy-7,11,TEXT,true);text(c,habits.get(i).goal,55,yy+6,8,MUTED,false);hits.add(new RectF(X(20),Y(yy-row/2),X(368),Y(yy+row/2)));}todayHit.set(X(18),Y(top),X(372),Y(bottom));
      float it=bottom+10;round(c,18,it,372,Math.min(navTop-14,it+55),16,SOFT);text(c,"↗",31,it+31,14,GREEN,true);text(c,"Seu ritmo está ficando mais consistente",56,it+24,11,TEXT,true);text(c,"Veja detalhes em Progresso",56,it+39,8,MUTED,false);insightHit.set(X(18),Y(it),X(372),Y(it+55)); }

    void progress(Canvas c){ hamburger(c,22,24);center(c,"Progresso",195,35,17,TEXT,true);text(c,"Visão geral",20,61,10,MUTED,false);
      card(c,18,75,372,215,16);text(c,"Consistência do mês",30,98,10,MUTED,false);text(c,monthPct()+"%",30,133,28,TEXT,true);text(c,"Hoje "+pct()+"%  •  Sequência "+(pct()>0?"1d":"0d")+"  •  Concluídos "+done(),30,154,9,GREEN,true);for(int i=0;i<3;i++)line(c,30,175+i*14,358,175+i*14,BORDER,.6f);float[] yy={201,194,187,180,184,176,179,169,171,160};Path path=new Path();for(int i=0;i<yy.length;i++){float xx=30+i*36.4f;if(i==0)path.moveTo(X(xx),Y(yy[i]));else path.lineTo(X(xx),Y(yy[i]));}p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(X(1.8f));p.setColor(GREEN);c.drawPath(path,p);
      card(c,18,228,372,394,16);text(c,"Calendário · Agosto 2026",30,252,12,TEXT,true);String[] wk={"D","S","T","Q","Q","S","S"};for(int i=0;i<7;i++)center(c,wk[i],52+i*48,276,7,MUTED,false);int day=1;for(int r=0;r<5;r++)for(int col=0;col<7;col++){if(r==0&&col<6)continue;if(day>31)continue;float x=52+col*48,y=303+r*22;if(day==16)round(c,x-13,y-13,x+13,y+8,12,SOFT);center(c,""+day,x,y,8,day==16?GREEN:MUTED,day==16);day++;}text(c,"Consistência do mês",30,379,8,MUTED,false);text(c,monthPct()+"%",340,379,10,GREEN,true);
      card(c,18,407,372,518,16);text(c,"Insights da Oliven",30,432,12,TEXT,true);text(c,"↗",30,459,13,GREEN,true);text(c,"Você é mais consistente nas segundas e terças.",52,458,9,TEXT,true);text(c,"◷",30,485,12,GREEN,true);text(c,"Suas noites após as 21h têm menor conclusão.",52,484,9,TEXT,true);text(c,"Meu ano",30,507,9,MUTED,true);text(c,"JAN 92%  FEV 81%  MAR 76%  ABR 88%  ·  AGO 82%",84,507,7.5f,GREEN,false); }

    void habitPage(Canvas c){text(c,"Hábitos",18,46,24,TEXT,true);text(c,"Meus hábitos",18,64,9,MUTED,false);text(c,"+",349,47,22,TEXT,true);String[] cats={"Todos","Corpo","Mente","Projetos","Pessoal"};for(int i=0;i<5;i++){float l=18+i*70;round(c,l,74,l+66,100,14,i==0?SOFT:WHITE);center(c,cats[i],l+33,92,8,i==0?GREEN:MUTED,i==0);}String[] ic={"◉","◆","●","▤","✓","♥","▤"};for(int i=0;i<7;i++){float t=112+i*57;card(c,18,t,372,t+50,15);round(c,30,t+8,65,t+42,11,SOFT);center(c,ic[i],47.5f,t+30,11,i==5?Color.rgb(230,54,69):GREEN,true);text(c,habits.get(i).name,77,t+24,11,TEXT,true);text(c,habits.get(i).goal,77,t+38,8,MUTED,false);text(c,"⋮",344,t+31,16,MUTED,false);}}

    void profile(Canvas c){hamburger(c,22,24);center(c,"Perfil",195,35,17,TEXT,true);card(c,18,48,372,112,16);p.setStyle(Paint.Style.FILL);p.setColor(GREEN);c.drawCircle(X(55),Y(80),X(22),p);center(c,"J",55,87,19,WHITE,true);text(c,"Jean Silva",92,78,12,TEXT,true);text(c,"Membro desde abr/2024",92,92,8,MUTED,false);String[][] rows={{"Dados pessoais","Nome, preferências e objetivo"},{"Preferências","Aparência e rotina"},{"Notificações","Lembretes da rotina"},{"Backup e sincronização","Em breve"},{"Ajuda e suporte","Central de ajuda"},{"Sobre a Oliven","Oliven 1.0.7 · Android nativo"}};float t=122;for(String[] r:rows){card(c,18,t,372,t+48,14);text(c,r[0],30,t+22,10.5f,TEXT,true);text(c,r[1],30,t+35,7.8f,MUTED,false);text(c,"›",344,t+31,17,MUTED,false);t+=56;}}

    void circlePage(Canvas c){text(c,"‹",18,37,23,TEXT,false);center(c,"Círculo",195,37,16,TEXT,true);center(c,"Agosto 2026",195,66,10.5f,TEXT,true);float cx=195,cy=197,r=83;for(int i=1;i<=31;i++){double a=Math.toRadians(-90+(i-1)*(360.0/31));float x=(float)(cx+Math.cos(a)*r),y=(float)(cy+Math.sin(a)*r);float total=24,prog=total*(dayPct(i)/100f);c.save();c.rotate((float)Math.toDegrees(a)+90,X(x),Y(y));round(c,x-5,y-total/2,x+5,y+total/2,2,LIGHT);if(prog>0){float start=y+total/2-prog;round(c,x-5,start,x+5,y+total/2,2,GREEN2);}c.restore();if(i%2==1){float tx=(float)(cx+Math.cos(a)*(r+20)),ty=(float)(cy+Math.sin(a)*(r+20));center(c,""+i,tx,ty+2,6.5f,MUTED,false);}}
      p.setStyle(Paint.Style.FILL);p.setColor(WHITE);c.drawCircle(X(cx),Y(cy),X(51),p);center(c,"16",cx,cy-2,28,TEXT,true);center(c,pct()+"% hoje",cx,cy+20,8,GREEN,true);card(c,18,310,372,506,15);text(c,"16 de agosto",30,334,11,TEXT,true);for(int i=0;i<5;i++){float y=364+i*29;check(c,36,y-4,isDoneToday(i));text(c,habits.get(i).name,56,y-6,10,TEXT,true);text(c,habits.get(i).goal,56,y+7,7.5f,MUTED,false);}}

    void myDay(Canvas c){text(c,"‹",18,37,23,TEXT,false);center(c,"Meu Dia",195,37,16,TEXT,true);text(c,"Hoje",24,72,18,TEXT,true);text(c,"Domingo, 16 de agosto",24,90,9,MUTED,false);text(c,done()+" de 5 concluídos",290,72,9,GREEN,true);card(c,18,108,372,396,16);for(int i=0;i<5;i++){float y=144+i*49;check(c,38,y,isDoneToday(i));text(c,habits.get(i).name,58,y-4,12,TEXT,true);text(c,habits.get(i).goal,58,y+11,8,MUTED,false);hits.add(new RectF(X(18),Y(y-22),X(372),Y(y+22)));}}

    void bottom(Canvas c){p.setStyle(Paint.Style.FILL);p.setColor(WHITE);c.drawRect(0,Y(navTop),getWidth(),getHeight(),p);line(c,0,navTop,390,navTop,BORDER,.6f);String[] n={"Hoje","Progresso","Hábitos","Perfil"};String[] ic={"⌂","↗","✓","♙"};for(int i=0;i<4;i++){float x=55+i*94;int active=(screen<=3?screen:(screen==4||screen==5?0:0));center(c,ic[i],x,navTop+25,15,i==active?GREEN:MUTED,i==active);center(c,n[i],x,navTop+45,8.5f,i==active?GREEN:MUTED,i==active);}}

    void drawer(Canvas c){round(c,18,54,230,190,14,WHITE);text(c,"Oliven",34,82,17,TEXT,true);String[] m={"Tela Inicial","Círculo","Meu Dia","Progresso"};for(int i=0;i<4;i++)text(c,m[i],34,111+i*24,11,TEXT,false);}

    @Override public boolean onTouchEvent(android.view.MotionEvent e){if(e.getAction()!=MotionEvent.ACTION_UP)return true;float x=e.getX(),y=e.getY();if(menu){if(x<X(230)&&y>Y(84)&&y<Y(190)){int idx=(int)((y/Y(1)-91)/24);if(idx<=0)screen=0;else if(idx==1)screen=4;else if(idx==2)screen=5;else screen=1;menu=false;invalidate();return true;}menu=false;invalidate();return true;}if(menuHit.contains(x,y)){menu=true;invalidate();return true;}if(y>Y(navTop)){int idx=Math.min(3,Math.max(0,(int)(x/(getWidth()/4f))));screen=idx;invalidate();return true;}if(screen==0){if(ringHit.contains(x,y)){screen=4;invalidate();return true;}if(insightHit.contains(x,y)){screen=1;invalidate();return true;}for(int i=0;i<hits.size()&&i<5;i++)if(hits.get(i).contains(x,y)){toggle(i);return true;}}else if(screen==4||screen==5){if(y<Y(60)){screen=0;invalidate();return true;}for(int i=0;i<hits.size()&&i<5;i++)if(hits.get(i).contains(x,y)){toggle(i);return true;}}return true;}
    void toggle(int i){boolean v=isDoneToday(i);prefs.edit().putBoolean(dateKey(now.get(Calendar.DAY_OF_MONTH),habits.get(i).id),!v).apply();invalidate();}
  }
}
