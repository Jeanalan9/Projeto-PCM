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
    getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR | View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR);
    setContentView(new OlivenView(this));
  }

  static class Habit{
    int id; String name, goal, cat, icon;
    Habit(int id,String name,String goal,String cat,String icon){this.id=id;this.name=name;this.goal=goal;this.cat=cat;this.icon=icon;}
  }

  static class OlivenView extends View{
    final int BG=Color.rgb(250,251,248), WHITE=Color.WHITE, TEXT=Color.rgb(24,30,26), MUTED=Color.rgb(100,108,102), GREEN=Color.rgb(32,112,76), GREEN_DARK=Color.rgb(17,84,55), GREEN_SOFT=Color.rgb(238,246,238), BORDER=Color.rgb(222,227,220), TRACK=Color.rgb(226,233,225), RED=Color.rgb(229,50,66);
    final Paint p=new Paint(Paint.ANTI_ALIAS_FLAG);
    final ArrayList<Habit> habits=new ArrayList<>();
    final ArrayList<RectF> rowHits=new ArrayList<>();
    final ArrayList<RectF> menuHits=new ArrayList<>();
    SharedPreferences prefs;
    Calendar now=Calendar.getInstance();
    float s=1f,H=820,navTop=750;
    int screen=0;
    boolean drawer=false;
    RectF menuBtn=new RectF(), ringHit=new RectF(), todayHit=new RectF(), insightHit=new RectF(), addHit=new RectF();

    OlivenView(Context c){
      super(c);
      setLayerType(View.LAYER_TYPE_SOFTWARE,null);
      prefs=c.getSharedPreferences("oliven",Context.MODE_PRIVATE);
      habits.add(new Habit(1,"Academia","0 / 60 min","Corpo","halter"));
      habits.add(new Habit(2,"Projeto Homem de Ferro","1h42 / 2h","Projetos","diamante"));
      habits.add(new Habit(3,"Beber água","3,2 / 3 litros","Corpo","gota"));
      habits.add(new Habit(4,"Leitura","0 / 30 min","Mente","livro"));
      habits.add(new Habit(5,"Organização","Concluída","Pessoal","check"));
      habits.add(new Habit(6,"Cardio","4x por semana","Corpo","coracao"));
      habits.add(new Habit(7,"Estudo","1h por dia","Mente","livro"));
    }

    float X(float v){return v*s;} float Y(float v){return v*s;}
    void calc(){s=getWidth()/390f; H=getHeight()/s; navTop=H-76; if(navTop<690) navTop=690;}
    String dateKey(int day,int id){Calendar c=(Calendar)now.clone(); c.set(Calendar.DAY_OF_MONTH,day); return "done_"+new SimpleDateFormat("yyyyMMdd",Locale.US).format(c.getTime())+"_"+id;}
    boolean doneToday(int i){return prefs.getBoolean(dateKey(now.get(Calendar.DAY_OF_MONTH),habits.get(i).id),false);}    
    int doneCount(){int d=0; for(int i=0;i<5;i++) if(doneToday(i)) d++; return d;}
    int todayPct(){return doneCount()*20;}
    int dayPct(int day){int d=0; for(int i=0;i<5;i++) if(prefs.getBoolean(dateKey(day,habits.get(i).id),false)) d++; return d*20;}
    boolean hasSavedDay(int day){for(int i=0;i<5;i++) if(prefs.contains(dateKey(day,habits.get(i).id))) return true; return false;}
    int monthPct(){int td=now.get(Calendar.DAY_OF_MONTH), sum=0; for(int d=1;d<=td;d++) sum+=dayPct(d); return td==0?0:Math.round(sum/(float)td);}    
    int weekPct(){int d=todayPct(); return d==0?0:Math.max(10,Math.round(d*0.55f));}
    int ninetyPct(){int m=monthPct(); return Math.max(0,Math.round(m*0.33f));}
    int blend(int a,int b,float t){int ar=Color.red(a),ag=Color.green(a),ab=Color.blue(a); int br=Color.red(b),bg=Color.green(b),bb=Color.blue(b); return Color.rgb((int)(ar+(br-ar)*t),(int)(ag+(bg-ag)*t),(int)(ab+(bb-ab)*t));}
    int pctColor(int pct){if(pct<=0)return Color.rgb(244,247,242); return blend(Color.rgb(226,241,229),GREEN,Math.min(1f,pct/100f));}

    void font(float size,int color,boolean bold){p.setTypeface(Typeface.create("sans",bold?Typeface.BOLD:Typeface.NORMAL)); p.setTextSize(X(size)); p.setColor(color); p.setStyle(Paint.Style.FILL); p.setTextAlign(Paint.Align.LEFT); p.clearShadowLayer();}
    void text(Canvas c,String t,float x,float y,float size,int color,boolean bold){font(size,color,bold); c.drawText(t,X(x),Y(y),p);}    
    void center(Canvas c,String t,float x,float y,float size,int color,boolean bold){font(size,color,bold); p.setTextAlign(Paint.Align.CENTER); c.drawText(t,X(x),Y(y),p); p.setTextAlign(Paint.Align.LEFT);}    
    void right(Canvas c,String t,float x,float y,float size,int color,boolean bold){font(size,color,bold); p.setTextAlign(Paint.Align.RIGHT); c.drawText(t,X(x),Y(y),p); p.setTextAlign(Paint.Align.LEFT);}    
    void line(Canvas c,float x1,float y1,float x2,float y2,int color,float w){p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(X(w)); p.setColor(color); p.setStrokeCap(Paint.Cap.ROUND); c.drawLine(X(x1),Y(y1),X(x2),Y(y2),p);}    
    void round(Canvas c,float l,float t,float r,float b,float rad,int color){p.setStyle(Paint.Style.FILL); p.setColor(color); p.clearShadowLayer(); c.drawRoundRect(new RectF(X(l),Y(t),X(r),Y(b)),X(rad),X(rad),p);}    
    void card(Canvas c,float l,float t,float r,float b,float rad){p.setStyle(Paint.Style.FILL); p.setColor(WHITE); p.setShadowLayer(X(2.4f),0,X(1.8f),0x14000000); c.drawRoundRect(new RectF(X(l),Y(t),X(r),Y(b)),X(rad),X(rad),p); p.clearShadowLayer(); p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(X(.8f)); p.setColor(BORDER); c.drawRoundRect(new RectF(X(l),Y(t),X(r),Y(b)),X(rad),X(rad),p);}    

    void drawLogo(Canvas c,float x,float y,float size){
      p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(X(size*.08f)); p.setColor(GREEN_DARK); p.setStrokeCap(Paint.Cap.ROUND);
      RectF rr=new RectF(X(x),Y(y),X(x+size),Y(y+size)); c.drawArc(rr,200,140,false,p); c.drawArc(rr,20,140,false,p);
      line(c,x+size*.12f,y+size*.50f,x+size*.38f,y+size*.50f,GREEN_DARK,size*.06f); line(c,x+size*.62f,y+size*.50f,x+size*.88f,y+size*.50f,GREEN_DARK,size*.06f);
      p.setStyle(Paint.Style.FILL); p.setColor(GREEN_DARK); c.drawCircle(X(x+size*.12f),Y(y+size*.50f),X(size*.055f),p); c.drawCircle(X(x+size*.38f),Y(y+size*.50f),X(size*.065f),p); c.drawCircle(X(x+size*.62f),Y(y+size*.50f),X(size*.065f),p); c.drawCircle(X(x+size*.88f),Y(y+size*.50f),X(size*.055f),p);
    }
    void hamburger(Canvas c,float x,float y){for(int i=0;i<3;i++) line(c,x,y+i*7,x+18,y+i*7,TEXT,1.7f); menuBtn.set(X(x-14),Y(y-18),X(x+40),Y(y+38));}
    void bell(Canvas c,float x,float y){p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(X(1.4f));p.setColor(TEXT);c.drawArc(new RectF(X(x-8),Y(y-7),X(x+8),Y(y+12)),200,140,false,p);line(c,x-9,y+11,x+9,y+11,TEXT,1.4f);p.setStyle(Paint.Style.FILL);p.setColor(RED);c.drawCircle(X(x+9),Y(y-7),X(3),p);}    

    void header(Canvas c){hamburger(c,22,29); drawLogo(c,76,18,24); text(c,"Oliven",106,39,21,GREEN_DARK,true); bell(c,350,30);}    
    void backHeader(Canvas c,String title){text(c,"‹",18,39,24,TEXT,false); center(c,title,195,38,17,TEXT,true);}    

    @Override protected void onDraw(Canvas c){
      super.onDraw(c); calc(); c.drawColor(BG); rowHits.clear(); menuHits.clear(); addHit.setEmpty();
      if(screen==0) home(c); else if(screen==1) progress(c); else if(screen==2) habits(c); else if(screen==3) profile(c); else if(screen==4) circle(c); else if(screen==5) myDay(c); else if(screen==6) calendar(c); else if(screen==7) insights(c); else if(screen==8) year(c);
      bottom(c); if(drawer) drawer(c);
    }

    void segmentedRing(Canvas c,float cx,float cy,float r,int value,float stroke){
      RectF rr=new RectF(X(cx-r),Y(cy-r),X(cx+r),Y(cy+r)); p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(X(stroke)); p.setStrokeCap(Paint.Cap.BUTT);
      int segs=78; int filled=Math.round(segs*value/100f);
      for(int i=0;i<segs;i++){p.setColor(i<filled?GREEN:TRACK); c.drawArc(rr,-90+i*(360f/segs),(360f/segs)*.58f,false,p);} p.setStrokeCap(Paint.Cap.ROUND);
    }
    void miniIcon(Canvas c,String icon,float cx,float cy,int color){
      p.setColor(color); p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(X(1.6f)); p.setStrokeCap(Paint.Cap.ROUND);
      if(icon.equals("halter")){line(c,cx-9,cy,cx+9,cy,color,1.6f); line(c,cx-11,cy-5,cx-11,cy+5,color,1.6f); line(c,cx+11,cy-5,cx+11,cy+5,color,1.6f);} 
      else if(icon.equals("gota")){Path path=new Path(); path.moveTo(X(cx),Y(cy-10)); path.quadTo(X(cx+10),Y(cy+2),X(cx),Y(cy+10)); path.quadTo(X(cx-10),Y(cy+2),X(cx),Y(cy-10)); c.drawPath(path,p);} 
      else if(icon.equals("livro")){p.setStyle(Paint.Style.STROKE); c.drawRect(X(cx-7),Y(cy-8),X(cx+7),Y(cy+8),p); line(c,cx-4,cy-4,cx+4,cy-4,color,1); line(c,cx-4,cy,cx+4,cy,color,1); line(c,cx-4,cy+4,cx+4,cy+4,color,1);} 
      else if(icon.equals("check")){line(c,cx-8,cy,cx-2,cy+6,color,2); line(c,cx-2,cy+6,cx+9,cy-8,color,2);} 
      else if(icon.equals("coracao")){p.setStyle(Paint.Style.FILL); p.setColor(RED); Path h=new Path(); h.moveTo(X(cx),Y(cy+8)); h.cubicTo(X(cx-16),Y(cy-1),X(cx-7),Y(cy-15),X(cx),Y(cy-6)); h.cubicTo(X(cx+7),Y(cy-15),X(cx+16),Y(cy-1),X(cx),Y(cy+8)); c.drawPath(h,p);} 
      else {p.setStyle(Paint.Style.FILL); c.drawCircle(X(cx),Y(cy),X(5),p);}    
    }
    void checkCircle(Canvas c,float x,float y,boolean done){p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(X(1.5f));p.setColor(done?GREEN:MUTED);c.drawCircle(X(x),Y(y),X(8.5f),p);if(done){p.setStyle(Paint.Style.FILL);p.setColor(GREEN);c.drawCircle(X(x),Y(y),X(7.2f),p);line(c,x-4,y,x-1,y+3,WHITE,1.5f);line(c,x-1,y+3,x+5,y-5,WHITE,1.5f);}}

    void home(Canvas c){
      header(c); text(c,"Bom dia, Jean",22,84,25,TEXT,true); text(c,"Domingo, 16 de agosto",22,105,12,MUTED,false);
      float cy=252, r=120; segmentedRing(c,195,cy,r,monthPct(),8.2f); center(c,monthPct()+"%",195,cy+4,43,TEXT,true); center(c,"Consistência",195,cy+27,12,MUTED,false); center(c,"deste mês",195,cy+43,12,MUTED,false); round(c,164,cy+57,226,cy+77,10,GREEN_SOFT); center(c,monthPct()>=80?"Excelente":"Em evolução",195,cy+71,9,GREEN,true); ringHit.set(X(60),Y(cy-r-8),X(330),Y(cy+r+12));
      float top=404, bottom=Math.min(navTop-112,662); card(c,22,top,368,bottom,18); text(c,"HOJE",38,top+31,13,TEXT,true); right(c,doneCount()+" de 5 concluídos",348,top+31,11,GREEN,true); float row=(bottom-top-72)/5f; for(int i=0;i<5;i++){float y=top+66+i*row; round(c,38,y-20,66,y+8,9,GREEN_SOFT); miniIcon(c,habits.get(i).icon,52,y-6,GREEN); text(c,habits.get(i).name,80,y-10,12,TEXT,true); text(c,habits.get(i).goal,80,y+6,9,MUTED,false); checkCircle(c,344,y-7,doneToday(i)); rowHits.add(new RectF(X(28),Y(y-row*.45f),X(360),Y(y+row*.45f))); } todayHit.set(X(22),Y(top),X(368),Y(bottom));
      float it=bottom+16; round(c,22,it,368,Math.min(navTop-16,it+66),18,GREEN_SOFT); text(c,"↗",42,it+39,23,GREEN,true); text(c,"Insight da Oliven",80,it+29,13,GREEN,true); text(c,"Você está construindo um ritmo mais forte.",80,it+47,9,TEXT,false); insightHit.set(X(22),Y(it),X(368),Y(it+66));
    }

    void progress(Canvas c){
      hamburger(c,22,29); center(c,"Evolução",195,39,18,TEXT,true);
      String[] tabs={"7 dias","30 dias","90 dias","1 ano"}; for(int i=0;i<4;i++){float l=22+i*86; round(c,l,60,l+78,89,16,i==1?GREEN_SOFT:WHITE); center(c,tabs[i],l+39,79,9,i==1?GREEN: MUTED,i==1);}      
      card(c,22,104,368,302,18); text(c,"Taxa de consistência",38,132,12,MUTED,false); text(c,monthPct()+"%",38,175,34,TEXT,true); text(c,"↑ 8% vs período anterior",38,197,10,GREEN,true); drawTrend(c,38,220,348,276);
      card(c,22,318,368,438,18); text(c,"Resumo",38,345,13,TEXT,true); summaryRow(c,"Hoje",todayPct()+"%",38,372); summaryRow(c,"Semana",weekPct()+"%",38,397); summaryRow(c,"Mês",monthPct()+"%",38,422);
      card(c,22,452,368,553,18); text(c,"Calendário",38,478,13,TEXT,true); text(c,"Agosto 2026",128,478,10,MUTED,false); drawMiniCalendar(c,38,497,312,72,true);
      card(c,22,568,368,navTop-14,18); text(c,"Insights e ano",38,594,13,TEXT,true); text(c,"↗",40,624,18,GREEN,true); text(c,"Você é mais consistente nas segundas e terças.",70,619,9.5f,TEXT,true); text(c,"AGO",40,657,8,MUTED,true); drawMonthCircle(c,82,651,23,82); text(c,"Mês atual",112,647,9,TEXT,true); text(c,"Seu ritmo mensal está em "+monthPct()+"%.",112,663,8,MUTED,false);
    }
    void drawTrend(Canvas c,float l,float t,float r,float b){for(int i=0;i<3;i++) line(c,l,t+14+i*18,r,t+14+i*18,BORDER,.6f); int base=monthPct(); float[] vals={20,31,42,55,47,60,56,70,67,82}; Path path=new Path(); for(int i=0;i<vals.length;i++){float v=Math.max(10,Math.min(100,(vals[i]+base*.18f)));float x=l+i*((r-l)/(vals.length-1));float y=b-(v/100f)*(b-t); if(i==0)path.moveTo(X(x),Y(y)); else path.lineTo(X(x),Y(y));} p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(X(2.2f));p.setColor(GREEN);p.setStrokeCap(Paint.Cap.ROUND);c.drawPath(path,p);}
    void summaryRow(Canvas c,String label,String val,float x,float y){text(c,label,x,y,10,TEXT,false); right(c,val,344,y,10,GREEN,true);}

    void habits(Canvas c){
      text(c,"Hábitos",22,58,27,TEXT,true); text(c,"Meus hábitos",22,78,10,MUTED,false); text(c,"+",350,56,26,TEXT,true); addHit.set(X(330),Y(20),X(382),Y(76)); String[] cats={"Todos","Corpo","Mente","Projetos","Pessoal"}; for(int i=0;i<5;i++){float l=22+i*70; round(c,l,94,l+65,124,16,i==0?GREEN_SOFT:WHITE); center(c,cats[i],l+32,113,8.5f,i==0?GREEN:MUTED,i==0);}
      float top=140; for(int i=0;i<7;i++){float y=top+i*67; card(c,22,y,368,y+58,16); round(c,36,y+11,78,y+47,12,GREEN_SOFT); miniIcon(c,habits.get(i).icon,57,y+29,i==5?RED:GREEN); text(c,habits.get(i).name,92,y+27,12.5f,TEXT,true); text(c,habits.get(i).cat+" • "+habits.get(i).goal,92,y+43,9,MUTED,false); text(c,"⋮",344,y+35,18,MUTED,false);}    
    }

    void profile(Canvas c){
      hamburger(c,22,29); center(c,"Perfil",195,39,18,TEXT,true); card(c,22,64,368,140,18); p.setStyle(Paint.Style.FILL);p.setColor(GREEN);c.drawCircle(X(62),Y(102),X(26),p);center(c,"J",62,112,22,WHITE,true);text(c,"Jean Silva",104,100,13,TEXT,true);text(c,"Membro desde abr/2024",104,117,8.5f,MUTED,false);
      String[][] rows={{"Dados pessoais","Nome, preferências e objetivo"},{"Preferências","Aparência e rotina"},{"Notificações","Lembretes da rotina"},{"Backup e sincronização","Em breve"},{"Ajuda e suporte","Central de ajuda"},{"Sobre a Oliven","Oliven 1.0.9 • Android nativo"}}; float y=156; String[] icons={"♙","⚙","♢","◉","?","?"}; for(int i=0;i<rows.length;i++){card(c,22,y,368,y+58,16); center(c,icons[i],48,y+35,14,MUTED,false); text(c,rows[i][0],76,y+26,12,TEXT,true); text(c,rows[i][1],76,y+42,8.5f,MUTED,false); text(c,"›",344,y+36,21,MUTED,false); y+=68;}    
    }

    void circle(Canvas c){
      backHeader(c,"Círculo"); text(c,"▣",350,38,13,TEXT,false); center(c,"Agosto 2026",195,74,12,TEXT,true); text(c,"‹",28,74,21,TEXT,false); right(c,"›",360,74,21,TEXT,false);
      float cx=195, cy=250, r=108; for(int i=1;i<=31;i++){double a=Math.toRadians(-90+(i-1)*(360.0/31)); float x=(float)(cx+Math.cos(a)*r), y=(float)(cy+Math.sin(a)*r); float total=36, w=12; int pct=dayPct(i); c.save(); c.rotate((float)Math.toDegrees(a)+90,X(x),Y(y)); round(c,x-w/2,y-total/2,x+w/2,y+total/2,3,TRACK); if(pct>0){float prog=total*pct/100f; round(c,x-w/2,y+total/2-prog,x+w/2,y+total/2,3,blend(Color.rgb(160,207,145),GREEN,pct/100f));} c.restore(); if(i%2==1){float tx=(float)(cx+Math.cos(a)*(r+24)), ty=(float)(cy+Math.sin(a)*(r+24)); center(c,""+i,tx,ty+3,7,MUTED,false);} }
      p.setStyle(Paint.Style.FILL);p.setColor(WHITE);p.setShadowLayer(X(1.6f),0,X(1),0x11000000);c.drawCircle(X(cx),Y(cy),X(62),p);p.clearShadowLayer();center(c,"16",cx,cy-2,36,TEXT,true);center(c,"AGO",cx,cy+24,11,MUTED,true);center(c,"Domingo",cx,cy+42,10,TEXT,false);
      card(c,22,396,368,navTop-18,18); text(c,"16 de agosto",38,424,13,TEXT,true); for(int i=0;i<5;i++){float y=458+i*44; checkCircle(c,48,y-5,doneToday(i)); text(c,habits.get(i).name,76,y-10,12,TEXT,true); text(c,habits.get(i).goal,76,y+6,8.5f,MUTED,false); checkCircle(c,344,y-5,doneToday(i)); rowHits.add(new RectF(X(26),Y(y-22),X(362),Y(y+20)));}
    }

    void myDay(Canvas c){
      backHeader(c,"Meu Dia"); text(c,"Hoje",26,84,22,TEXT,true); text(c,"Domingo, 16 de agosto",26,104,10,MUTED,false); right(c,doneCount()+" de 5 concluídos",350,84,10,GREEN,true); card(c,22,128,368,500,18); for(int i=0;i<5;i++){float y=178+i*64; checkCircle(c,48,y,doneToday(i)); text(c,habits.get(i).name,76,y-7,14,TEXT,true); text(c,habits.get(i).goal,76,y+13,9,MUTED,false); rowHits.add(new RectF(X(26),Y(y-28),X(362),Y(y+28)));} round(c,22,526,368,596,18,GREEN_SOFT); text(c,"★",44,570,21,GREEN,true); text(c,"Pequenas ações, grandes",86,558,13,TEXT,true); text(c,"resultados no final do dia.",86,578,13,TEXT,true);
    }

    void calendar(Canvas c){
      backHeader(c,"Calendário"); text(c,"‹",28,75,21,TEXT,false); right(c,"›",360,75,21,TEXT,false); center(c,"Agosto 2026",195,75,12,TEXT,true); drawLargeCalendar(c,30,112,330,292); card(c,22,486,368,562,18); text(c,monthPct()+"%",44,535,28,GREEN,true); text(c,"Consistência do mês",126,526,12,TEXT,false); text(c,"Dias passados coloridos pela porcentagem atingida",126,544,8.5f,MUTED,false); round(c,22,586,368,navTop-18,18,GREEN_SOFT); text(c,"Quanto mais forte o verde, maior foi a execução daquele dia.",42,624,10,TEXT,false);
    }

    void insights(Canvas c){
      backHeader(c,"Insights da Oliven"); insightCard(c,22,86,368,180,"↗","Você é mais consistente","nas segundas e terças.","Taxa média nesses dias: 87%"); insightCard(c,22,204,368,298,"◷","Suas noites após as 21h","têm menor conclusão.","Considere ajustar sua rotina."); insightCard(c,22,322,368,416,"↗","Seu desempenho geral","melhorou 8% este mês.","Continue evoluindo!"); round(c,22,444,368,502,16,GREEN_SOFT); text(c,"Ver todos os insights",40,479,11,TEXT,false); text(c,"›",344,480,21,MUTED,false); }
    void insightCard(Canvas c,float l,float t,float r,float b,String ic,String a,String b1,String sub){card(c,l,t,r,b,16);text(c,ic,l+28,t+55,22,GREEN,true);text(c,a,l+78,t+40,12,TEXT,true);text(c,b1,l+78,t+59,12,TEXT,true);text(c,sub,l+78,t+79,8.5f,MUTED,false);}

    void year(Canvas c){
      backHeader(c,"Meu ano em 2026"); text(c,"›",350,39,24,TEXT,false); String[] ms={"JAN","FEV","MAR","ABR","MAI","JUN","JUL","AGO","SET","OUT","NOV","DEZ"}; int[] vals={92,81,76,88,73,84,79,82,0,0,0,0}; for(int i=0;i<12;i++){float x=62+(i%4)*88, y=140+(i/4)*130; center(c,ms[i],x,y-34,9,MUTED,true); drawMonthCircle(c,x,y,31,vals[i]); center(c,vals[i]>0?vals[i]+"%":"-",x,y+5,11,TEXT,true);} round(c,22,560,368,navTop-18,18,GREEN_SOFT); text(c,"Visão anual",42,596,13,GREEN,true); text(c,"Acompanhe a consistência mês a mês sem excesso de informação.",42,617,9,TEXT,false);}
    void drawMonthCircle(Canvas c,float x,float y,float r,int pct){p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(X(2.2f));p.setColor(pct>0?GREEN:TRACK);c.drawCircle(X(x),Y(y),X(r),p);if(pct>0){p.setStrokeWidth(X(4));c.drawArc(new RectF(X(x-r),Y(y-r),X(x+r),Y(y+r)),-90,360*pct/100f,false,p);}}

    void drawLargeCalendar(Canvas c,float l,float t,float w,float h){String[] wk={"D","S","T","Q","Q","S","S"}; for(int i=0;i<7;i++) center(c,wk[i],l+i*w/6f,t,9,MUTED,true); int day=1; for(int row=0;row<6;row++){for(int col=0;col<7;col++){if(row==0&&col<6)continue; if(day>31)continue; float x=l+col*w/6f, y=t+38+row*42; drawCalendarDay(c,x,y,day,17); day++;}}}
    void drawMiniCalendar(Canvas c,float l,float t,float w,float h,boolean compact){String[] wk={"D","S","T","Q","Q","S","S"}; for(int i=0;i<7;i++) center(c,wk[i],l+i*w/6f,t,6.5f,MUTED,true); int day=1; for(int row=0;row<5;row++){for(int col=0;col<7;col++){if(row==0&&col<6)continue; if(day>31)continue; float x=l+col*w/6f, y=t+18+row*13; drawCalendarDay(c,x,y,day,8); day++;}}}
    void drawCalendarDay(Canvas c,float x,float y,int day,float rr){int td=now.get(Calendar.DAY_OF_MONTH); int pct=day<=td?dayPct(day):0; boolean today=day==td; int col=day<=td?pctColor(pct):Color.TRANSPARENT; if(day<=td){p.setStyle(Paint.Style.FILL);p.setColor(col);c.drawCircle(X(x),Y(y),X(today?rr+2:rr),p);} if(today){p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(X(1.6f));p.setColor(GREEN);c.drawCircle(X(x),Y(y),X(rr+3),p);} center(c,""+day,x,y+4,rr>10?9:6.5f,(pct>=60||today)?GREEN_DARK:MUTED,today||pct>=80);}    

    void bottom(Canvas c){float top=navTop; p.setStyle(Paint.Style.FILL);p.setColor(WHITE);c.drawRect(0,Y(top),getWidth(),getHeight(),p); line(c,0,top,390,top,BORDER,.6f); String[] labs={"Hoje","Progresso","Hábitos","Perfil"}; String[] ic={"⌂","↗","✓","♙"}; for(int i=0;i<4;i++){float cx=49+i*97; boolean active=screen==i || (screen>=4 && i==0); center(c,ic[i],cx,top+28,19,active?GREEN:MUTED,true); center(c,labs[i],cx,top+52,9.8f,active?GREEN:MUTED,active); if(active) round(c,cx-17,top+62,cx+17,top+65,2,GREEN);} }

    void drawer(Canvas c){
      p.setStyle(Paint.Style.FILL); p.setColor(0x77000000); c.drawRect(X(272),0,getWidth(),getHeight(),p); round(c,0,0,272,H,0,WHITE); drawLogo(c,22,36,26); text(c,"Oliven",58,58,21,GREEN_DARK,true); String[] items={"Tela Inicial","Círculo","Evolução","Meu Dia","Hábitos","Calendário","Insights da Oliven","Meu Ano","Perfil"}; int[] sc={0,4,1,5,2,6,7,8,3}; float y=104; for(int i=0;i<items.length;i++){boolean active=screen==sc[i]; if(active) round(c,16,y-23,256,y+13,14,GREEN_SOFT); text(c,drawerIcon(i),34,y,14,active?GREEN:MUTED,false); text(c,items[i],68,y,11,active?GREEN:TEXT,active); menuHits.add(new RectF(X(0),Y(y-28),X(272),Y(y+20))); y+=45;} round(c,16,H-98,256,H-22,16,GREEN_SOFT); drawLogo(c,34,H-78,24); text(c,"Evolua todos os dias.",72,H-68,11,GREEN_DARK,true); text(c,"O progresso é construído",72,H-50,8,TEXT,false); text(c,"nos detalhes.",72,H-36,8,TEXT,false);
    }
    String drawerIcon(int i){String[] a={"⌂","◷","↗","☑","✦","▣","◷","▧","♙"};return a[i];}

    @Override public boolean onTouchEvent(android.view.MotionEvent e){
      if(e.getAction()!=MotionEvent.ACTION_UP) return true; float dx=e.getX(), dy=e.getY(), x=dx/s, y=dy/s;
      if(drawer){ for(int i=0;i<menuHits.size();i++){if(menuHits.get(i).contains(dx,dy)){int[] sc={0,4,1,5,2,6,7,8,3}; screen=sc[i]; drawer=false; invalidate(); return true;}} drawer=false; invalidate(); return true; }
      if(menuBtn.contains(dx,dy)){drawer=true; invalidate(); return true;}
      if(y>navTop){int idx=(int)(x/97); if(idx<0)idx=0; if(idx>3)idx=3; screen=idx; invalidate(); return true;}
      if(screen==0){ if(ringHit.contains(dx,dy)){screen=4; invalidate(); return true;} if(insightHit.contains(dx,dy)){screen=7; invalidate(); return true;} }
      if(screen==0 || screen==4 || screen==5){ for(int i=0;i<rowHits.size() && i<5;i++){if(rowHits.get(i).contains(dx,dy)){String k=dateKey(now.get(Calendar.DAY_OF_MONTH),habits.get(i).id); prefs.edit().putBoolean(k,!prefs.getBoolean(k,false)).apply(); invalidate(); return true;}} }
      if(screen>=4 && x<56 && y<60){screen=0; invalidate(); return true;}
      return true;
    }
  }
}
