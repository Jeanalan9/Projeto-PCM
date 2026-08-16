package com.oliven.app;

import android.app.*;
import android.os.*;
import android.content.*;
import android.graphics.*;
import android.graphics.drawable.*;
import android.view.*;
import android.widget.*;
import java.text.*;
import java.util.*;

public class MainActivity extends Activity {
    static final int BG=Color.rgb(248,249,245), WHITE=Color.WHITE, TEXT=Color.rgb(25,31,26), MUTED=Color.rgb(111,118,111), GREEN=Color.rgb(73,111,64), GREEN_DARK=Color.rgb(25,67,48), GREEN_SOFT=Color.rgb(233,240,226), BORDER=Color.rgb(223,226,218);
    LinearLayout root, content, nav;
    SharedPreferences prefs;
    ArrayList<Habit> habits=new ArrayList<>();
    Calendar now=Calendar.getInstance();
    int active=0;

    @Override public void onCreate(Bundle state){
        super.onCreate(state);
        getWindow().setStatusBarColor(BG);
        getWindow().setNavigationBarColor(WHITE);
        getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR | View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR);
        prefs=getSharedPreferences("oliven",MODE_PRIVATE);
        loadHabits();
        root=new LinearLayout(this); root.setOrientation(LinearLayout.VERTICAL); root.setBackgroundColor(BG);
        content=new LinearLayout(this); content.setOrientation(LinearLayout.VERTICAL);
        root.addView(content,new LinearLayout.LayoutParams(-1,0,1));
        nav=buildNav(); root.addView(nav,new LinearLayout.LayoutParams(-1,dp(70)));
        setContentView(root);
        switchTab(0);
    }

    int dp(int v){ return (int)(v*getResources().getDisplayMetrics().density+.5f); }
    TextView text(String s,float sp,int color,boolean bold){ TextView v=new TextView(this); v.setText(s); v.setTextSize(sp); v.setTextColor(color); v.setGravity(Gravity.CENTER_VERTICAL); if(bold)v.setTypeface(Typeface.DEFAULT,Typeface.BOLD); return v; }
    GradientDrawable shape(int color,int radius){ GradientDrawable g=new GradientDrawable();g.setColor(color);g.setCornerRadius(dp(radius));return g; }
    GradientDrawable cardShape(){ GradientDrawable g=shape(WHITE,22);g.setStroke(dp(1),BORDER);return g; }
    LinearLayout card(){ LinearLayout c=new LinearLayout(this);c.setOrientation(LinearLayout.VERTICAL);c.setPadding(dp(20),dp(18),dp(20),dp(18));c.setBackground(cardShape());return c; }
    Space gap(int h){ Space s=new Space(this);s.setLayoutParams(new LinearLayout.LayoutParams(1,dp(h)));return s; }
    void margins(View v,int l,int t,int r,int b){ ViewGroup.LayoutParams base=v.getLayoutParams(); LinearLayout.LayoutParams p=base instanceof LinearLayout.LayoutParams?(LinearLayout.LayoutParams)base:new LinearLayout.LayoutParams(-1,-2);p.setMargins(dp(l),dp(t),dp(r),dp(b));v.setLayoutParams(p); }

    LinearLayout buildNav(){
        LinearLayout bar=new LinearLayout(this);bar.setOrientation(LinearLayout.HORIZONTAL);bar.setGravity(Gravity.CENTER);bar.setPadding(dp(8),dp(5),dp(8),dp(4));bar.setBackgroundColor(WHITE);
        String[] labels={"Hoje","Progresso","Hábitos","Perfil"};
        for(int i=0;i<4;i++){
            final int ix=i;LinearLayout cell=new LinearLayout(this);cell.setOrientation(LinearLayout.VERTICAL);cell.setGravity(Gravity.CENTER);
            NavIcon icon=new NavIcon(this,i);icon.setTag("icon"+i);cell.addView(icon,new LinearLayout.LayoutParams(dp(27),dp(27)));
            TextView label=text(labels[i],11,i==0?GREEN:MUTED,false);label.setGravity(Gravity.CENTER);label.setTag("label"+i);cell.addView(label,new LinearLayout.LayoutParams(-1,dp(25)));
            cell.setOnClickListener(v->switchTab(ix));bar.addView(cell,new LinearLayout.LayoutParams(0,-1,1));
        }return bar;
    }
    void switchTab(int tab){
        active=tab;
        for(int i=0;i<4;i++){ NavIcon ic=nav.findViewWithTag("icon"+i);TextView tx=nav.findViewWithTag("label"+i);if(ic!=null){ic.active=i==tab;ic.invalidate();}if(tx!=null)tx.setTextColor(i==tab?GREEN:MUTED); }
        if(tab==0)showHome(); else if(tab==1)showProgress(); else if(tab==2)showHabits(); else showProfile();
    }
    ScrollView screen(){ content.removeAllViews();ScrollView sc=new ScrollView(this);sc.setFillViewport(true);sc.setOverScrollMode(View.OVER_SCROLL_NEVER);LinearLayout body=new LinearLayout(this);body.setTag("body");body.setOrientation(LinearLayout.VERTICAL);body.setPadding(dp(24),dp(18),dp(24),dp(28));body.setBackgroundColor(BG);sc.addView(body,new ScrollView.LayoutParams(-1,-2));content.addView(sc,new LinearLayout.LayoutParams(-1,-1));return sc; }
    LinearLayout body(ScrollView sc){return (LinearLayout)sc.findViewWithTag("body");}

    LinearLayout header(String title,String subtitle,boolean branded){
        LinearLayout out=new LinearLayout(this);out.setOrientation(LinearLayout.VERTICAL);
        if(branded){ LinearLayout row=new LinearLayout(this);row.setGravity(Gravity.CENTER_VERTICAL);ImageView logo=new ImageView(this);logo.setImageResource(R.drawable.oliven_logo);row.addView(logo,new LinearLayout.LayoutParams(dp(34),dp(34)));TextView brand=text("Oliven",21,GREEN_DARK,true);row.addView(brand,new LinearLayout.LayoutParams(-2,dp(34)));margins(brand,8,0,0,0);out.addView(row);out.addView(gap(14)); }
        out.addView(text(title,32,TEXT,true)); if(subtitle!=null){TextView s=text(subtitle,16,MUTED,false);out.addView(s);margins(s,0,2,0,0);}return out;
    }
    String datePt(){String[] d={"Domingo","Segunda-feira","Terça-feira","Quarta-feira","Quinta-feira","Sexta-feira","Sábado"};String[] m={"janeiro","fevereiro","março","abril","maio","junho","julho","agosto","setembro","outubro","novembro","dezembro"};return d[now.get(Calendar.DAY_OF_WEEK)-1]+", "+now.get(Calendar.DAY_OF_MONTH)+" de "+m[now.get(Calendar.MONTH)];}
    String dayKey(Calendar c){return new SimpleDateFormat("yyyyMMdd",Locale.US).format(c.getTime());}
    int completed(Calendar c){int n=0;String k=dayKey(c);for(Habit h:habits)if(prefs.getBoolean("done_"+k+"_"+h.id,false))n++;return n;}
    int percent(Calendar c){return habits.size()==0?0:(int)Math.round(completed(c)*100.0/habits.size());}

    void showHome(){
        ScrollView sc=screen();LinearLayout b=body(sc);b.addView(header("Bom dia, Jean",datePt(),true));b.addView(gap(12));
        RingView ring=new RingView(this);ring.progress=percent(now);b.addView(ring,new LinearLayout.LayoutParams(-1,dp(240)));
        LinearLayout c=card();LinearLayout head=new LinearLayout(this);head.setGravity(Gravity.CENTER_VERTICAL);head.addView(text("Hoje",19,TEXT,true),new LinearLayout.LayoutParams(0,dp(34),1));TextView count=text(completed(now)+" de "+habits.size()+" concluídos",13,GREEN,true);count.setGravity(Gravity.RIGHT|Gravity.CENTER_VERTICAL);head.addView(count,new LinearLayout.LayoutParams(-2,dp(34)));c.addView(head);for(Habit h:habits)c.addView(checkRow(h));b.addView(c);margins(c,0,4,0,0);
        LinearLayout insight=card();insight.setBackground(shape(GREEN_SOFT,22));insight.addView(text("↗  Insight da Oliven",16,GREEN,true));TextView msg=text(percent(now)==100?"Excelente. Seu dia está completo.":"Comece pequeno: marque uma atividade e construa o restante do dia a partir dela.",15,TEXT,false);msg.setPadding(0,dp(8),0,0);insight.addView(msg);b.addView(insight);margins(insight,0,14,0,0);
    }
    View checkRow(Habit h){
        LinearLayout row=new LinearLayout(this);row.setGravity(Gravity.CENTER_VERTICAL);row.setPadding(0,dp(9),0,dp(9));String key="done_"+dayKey(now)+"_"+h.id;boolean done=prefs.getBoolean(key,false);
        StatusDot dot=new StatusDot(this,done);row.addView(dot,new LinearLayout.LayoutParams(dp(42),dp(44)));
        LinearLayout tx=new LinearLayout(this);tx.setOrientation(LinearLayout.VERTICAL);tx.addView(text(h.name,16,TEXT,true));tx.addView(text(h.goal,13,MUTED,false));row.addView(tx,new LinearLayout.LayoutParams(0,dp(46),1));
        row.setOnClickListener(v->{prefs.edit().putBoolean(key,!prefs.getBoolean(key,false)).apply();showHome();});return row;
    }

    void showProgress(){
        ScrollView sc=screen();LinearLayout b=body(sc);b.addView(header("Progresso","Sua evolução de forma simples.",false));b.addView(gap(20));
        LinearLayout hero=card();hero.addView(text("Consistência deste mês",15,MUTED,false));hero.addView(text(monthConsistency()+"%",40,TEXT,true));hero.addView(text("↑ evolução do seu ritmo",14,GREEN,true));TrendView trend=new TrendView(this);hero.addView(trend,new LinearLayout.LayoutParams(-1,dp(112)));b.addView(hero);
        LinearLayout grid=new LinearLayout(this);grid.setOrientation(LinearLayout.HORIZONTAL);LinearLayout a=new LinearLayout(this);a.setOrientation(LinearLayout.VERTICAL);LinearLayout d=new LinearLayout(this);d.setOrientation(LinearLayout.VERTICAL);a.addView(metric("Hoje",percent(now)+"%"));a.addView(metric("Sequência",streak()+" dias"));d.addView(metric("7 dias",last7()+"%"));d.addView(metric("Concluídos",String.valueOf(totalCompleted())));grid.addView(a,new LinearLayout.LayoutParams(0,-2,1));grid.addView(d,new LinearLayout.LayoutParams(0,-2,1));b.addView(grid);margins(grid,-5,12,-5,0);
        LinearLayout cal=card();cal.addView(text("Calendário",21,TEXT,true));cal.addView(text(monthName()+" "+now.get(Calendar.YEAR),14,MUTED,false));cal.addView(gap(10));cal.addView(calendarView());b.addView(cal);margins(cal,0,12,0,0);
        LinearLayout year=card();year.addView(text("Meu ano",21,TEXT,true));year.addView(gap(10));year.addView(yearView());b.addView(year);margins(year,0,12,0,0);
    }
    View metric(String label,String value){LinearLayout c=card();c.setPadding(dp(16),dp(15),dp(16),dp(15));c.addView(text(label,14,MUTED,false));c.addView(text(value,27,TEXT,true));margins(c,5,0,5,10);return c;}
    String monthName(){String[] m={"Janeiro","Fevereiro","Março","Abril","Maio","Junho","Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"};return m[now.get(Calendar.MONTH)];}
    View calendarView(){
        GridLayout g=new GridLayout(this);g.setColumnCount(7);String[] wk={"D","S","T","Q","Q","S","S"};for(String x:wk){TextView v=text(x,12,MUTED,false);v.setGravity(Gravity.CENTER);g.addView(v);gridCell(v);}
        Calendar first=(Calendar)now.clone();first.set(Calendar.DAY_OF_MONTH,1);for(int i=0;i<first.get(Calendar.DAY_OF_WEEK)-1;i++){TextView v=text("",12,MUTED,false);g.addView(v);gridCell(v);}int max=now.getActualMaximum(Calendar.DAY_OF_MONTH);
        for(int n=1;n<=max;n++){Calendar c=(Calendar)now.clone();c.set(Calendar.DAY_OF_MONTH,n);int p=percent(c);TextView v=text(String.valueOf(n),13,p>0?GREEN:MUTED,p>=80);v.setGravity(Gravity.CENTER);if(n==now.get(Calendar.DAY_OF_MONTH)){v.setBackground(shape(GREEN_SOFT,24));v.setTextColor(GREEN_DARK);}g.addView(v);gridCell(v);}return g;
    }
    void gridCell(View v){GridLayout.LayoutParams p=new GridLayout.LayoutParams();p.width=0;p.height=dp(43);p.columnSpec=GridLayout.spec(GridLayout.UNDEFINED,1f);v.setLayoutParams(p);}
    View yearView(){GridLayout g=new GridLayout(this);g.setColumnCount(4);String[] m={"JAN","FEV","MAR","ABR","MAI","JUN","JUL","AGO","SET","OUT","NOV","DEZ"};for(int i=0;i<12;i++){LinearLayout cell=new LinearLayout(this);cell.setOrientation(LinearLayout.VERTICAL);cell.setGravity(Gravity.CENTER);cell.addView(text(m[i],10,MUTED,true));CirclePercent cp=new CirclePercent(this);if(i==now.get(Calendar.MONTH)){cp.progress=monthConsistency();cp.label=monthConsistency()+"%";}cell.addView(cp,new LinearLayout.LayoutParams(dp(62),dp(62)));g.addView(cell);GridLayout.LayoutParams p=new GridLayout.LayoutParams();p.width=0;p.height=dp(86);p.columnSpec=GridLayout.spec(GridLayout.UNDEFINED,1f);cell.setLayoutParams(p);}return g;}

    void showHabits(){
        ScrollView sc=screen();LinearLayout b=body(sc);LinearLayout top=new LinearLayout(this);top.setGravity(Gravity.CENTER_VERTICAL);top.addView(header("Hábitos","Construa sua rotina no seu ritmo.",false),new LinearLayout.LayoutParams(0,-2,1));TextView add=text("+",34,WHITE,false);add.setGravity(Gravity.CENTER);add.setBackground(shape(GREEN,19));add.setOnClickListener(v->addDialog());top.addView(add,new LinearLayout.LayoutParams(dp(60),dp(60)));b.addView(top);b.addView(gap(18));
        LinearLayout chips=new LinearLayout(this);String[] names={"Todos","Corpo","Mente","Projetos","Pessoal"};for(String x:names){TextView chip=text(x,11,x.equals("Todos")?GREEN_DARK:MUTED,x.equals("Todos"));chip.setGravity(Gravity.CENTER);chip.setBackground(shape(x.equals("Todos")?GREEN_SOFT:WHITE,16));chip.setPadding(dp(10),0,dp(10),0);chips.addView(chip,new LinearLayout.LayoutParams(-2,dp(33)));margins(chip,0,0,6,0);}b.addView(chips);
        for(Habit h:habits){LinearLayout c=card();c.setOrientation(LinearLayout.HORIZONTAL);c.setGravity(Gravity.CENTER_VERTICAL);TextView ic=text(h.icon,18,GREEN,true);ic.setGravity(Gravity.CENTER);ic.setBackground(shape(GREEN_SOFT,18));c.addView(ic,new LinearLayout.LayoutParams(dp(46),dp(46)));LinearLayout tx=new LinearLayout(this);tx.setOrientation(LinearLayout.VERTICAL);tx.addView(text(h.name,17,TEXT,true));tx.addView(text(h.category+" • "+h.goal,13,MUTED,false));c.addView(tx,new LinearLayout.LayoutParams(0,-2,1));margins(tx,12,0,8,0);TextView menu=text("⋮",24,MUTED,false);menu.setGravity(Gravity.CENTER);menu.setOnClickListener(v->removeDialog(h));c.addView(menu,new LinearLayout.LayoutParams(dp(38),dp(48)));b.addView(c);margins(c,0,10,0,0);}
    }
    void addDialog(){LinearLayout form=new LinearLayout(this);form.setOrientation(LinearLayout.VERTICAL);form.setPadding(dp(18),0,dp(18),0);EditText n=new EditText(this);n.setHint("Nome do hábito");EditText g=new EditText(this);g.setHint("Meta");form.addView(n);form.addView(g);new AlertDialog.Builder(this).setTitle("Novo hábito").setView(form).setNegativeButton("Cancelar",null).setPositiveButton("Adicionar",(d,w)->{String name=n.getText().toString().trim(),goal=g.getText().toString().trim();if(name.length()==0)return;if(goal.length()==0)goal="Diário";habits.add(new Habit(System.currentTimeMillis(),name,goal,"Pessoal","✓"));saveHabits();showHabits();}).show();}
    void removeDialog(Habit h){new AlertDialog.Builder(this).setTitle("Remover hábito?").setMessage(h.name).setNegativeButton("Cancelar",null).setPositiveButton("Remover",(d,w)->{habits.remove(h);saveHabits();showHabits();}).show();}

    void showProfile(){
        ScrollView sc=screen();LinearLayout b=body(sc);b.addView(header("Perfil","Sua experiência na Oliven.",false));b.addView(gap(20));LinearLayout user=card();user.setOrientation(LinearLayout.HORIZONTAL);user.setGravity(Gravity.CENTER_VERTICAL);TextView avatar=text("J",29,WHITE,true);avatar.setGravity(Gravity.CENTER);avatar.setBackground(shape(GREEN,45));user.addView(avatar,new LinearLayout.LayoutParams(dp(76),dp(76)));LinearLayout tx=new LinearLayout(this);tx.setOrientation(LinearLayout.VERTICAL);tx.addView(text("Jean",21,TEXT,true));tx.addView(text("Evolua todos os dias.",14,MUTED,false));user.addView(tx,new LinearLayout.LayoutParams(0,-2,1));margins(tx,16,0,0,0);b.addView(user);
        b.addView(setting("Dados pessoais","Nome, preferências e objetivo"));b.addView(setting("Notificações","Lembretes da sua rotina"));b.addView(setting("Backup e sincronização","Em breve"));b.addView(setting("Privacidade","Seus dados permanecem neste aparelho"));b.addView(setting("Sobre a Oliven","Oliven 1.0.2 • Android nativo"));
    }
    View setting(String title,String sub){LinearLayout c=card();c.setOrientation(LinearLayout.HORIZONTAL);c.setGravity(Gravity.CENTER_VERTICAL);LinearLayout tx=new LinearLayout(this);tx.setOrientation(LinearLayout.VERTICAL);tx.addView(text(title,16,TEXT,true));tx.addView(text(sub,13,MUTED,false));c.addView(tx,new LinearLayout.LayoutParams(0,-2,1));TextView arrow=text("›",27,MUTED,false);arrow.setGravity(Gravity.CENTER);c.addView(arrow,new LinearLayout.LayoutParams(dp(26),dp(45)));margins(c,0,10,0,0);return c;}

    int monthConsistency(){int days=now.get(Calendar.DAY_OF_MONTH),sum=0;Calendar c=(Calendar)now.clone();for(int i=1;i<=days;i++){c.set(Calendar.DAY_OF_MONTH,i);sum+=percent(c);}return days==0?0:sum/days;}
    int last7(){int sum=0;Calendar c=(Calendar)now.clone();for(int i=0;i<7;i++){sum+=percent(c);c.add(Calendar.DAY_OF_MONTH,-1);}return sum/7;}
    int totalCompleted(){int total=0;Calendar c=(Calendar)now.clone();for(int i=1;i<=now.get(Calendar.DAY_OF_MONTH);i++){c.set(Calendar.DAY_OF_MONTH,i);total+=completed(c);}return total;}
    int streak(){int s=0;Calendar c=(Calendar)now.clone();for(int i=0;i<365;i++){if(percent(c)>=80)s++;else if(i>0)break;c.add(Calendar.DAY_OF_MONTH,-1);}return s;}
    void loadHabits(){String raw=prefs.getString("habits",null);if(raw==null){habits.add(new Habit(1,"Academia","5x por semana","Corpo","✦"));habits.add(new Habit(2,"Projeto pessoal","2h por dia","Projetos","◆"));habits.add(new Habit(3,"Beber água","3 litros por dia","Corpo","●"));habits.add(new Habit(4,"Leitura","30 min por dia","Mente","▤"));habits.add(new Habit(5,"Organização","Diário","Pessoal","✓"));return;}for(String line:raw.split("\\n")){String[] p=line.split("\\|",-1);if(p.length>=5)try{habits.add(new Habit(Long.parseLong(p[0]),p[1],p[2],p[3],p[4]));}catch(Exception ignored){}}}
    void saveHabits(){StringBuilder s=new StringBuilder();for(Habit h:habits)s.append(h.id).append("|").append(h.name.replace("|","")).append("|").append(h.goal.replace("|","")).append("|").append(h.category).append("|").append(h.icon).append("\n");prefs.edit().putString("habits",s.toString()).apply();}
    static class Habit{long id;String name,goal,category,icon;Habit(long i,String n,String g,String c,String x){id=i;name=n;goal=g;category=c;icon=x;}}

    class RingView extends View{Paint p=new Paint(1);int progress;RingView(Context c){super(c);}protected void onDraw(Canvas c){float cx=getWidth()/2f,cy=getHeight()/2f,r=Math.min(getWidth(),getHeight())*.34f;p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(dp(11));p.setStrokeCap(Paint.Cap.BUTT);p.setColor(Color.rgb(227,232,223));for(int i=0;i<60;i++)c.drawArc(cx-r,cy-r,cx+r,cy+r,-90+i*6,4,false,p);p.setColor(GREEN);int seg=(int)Math.round(progress*.6);for(int i=0;i<seg;i++)c.drawArc(cx-r,cy-r,cx+r,cy+r,-90+i*6,4,false,p);p.setStyle(Paint.Style.FILL);p.setTextAlign(Paint.Align.CENTER);p.setTypeface(Typeface.DEFAULT_BOLD);p.setTextSize(dp(46));p.setColor(TEXT);c.drawText(progress+"%",cx,cy+dp(7),p);p.setTypeface(Typeface.DEFAULT);p.setTextSize(dp(14));p.setColor(MUTED);c.drawText("Consistência de hoje",cx,cy+dp(34),p);}}
    class StatusDot extends View{Paint p=new Paint(1);boolean done;StatusDot(Context c,boolean d){super(c);done=d;}protected void onDraw(Canvas c){float x=getWidth()/2f,y=getHeight()/2f;p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(dp(2));p.setColor(done?GREEN:MUTED);c.drawCircle(x,y,dp(8),p);if(done){p.setStyle(Paint.Style.FILL);p.setTextAlign(Paint.Align.CENTER);p.setTypeface(Typeface.DEFAULT_BOLD);p.setTextSize(dp(12));p.setColor(GREEN);c.drawText("✓",x,y+dp(4),p);}}}
    class CirclePercent extends View{Paint p=new Paint(1);int progress=0;String label="—";CirclePercent(Context c){super(c);}protected void onDraw(Canvas c){float x=getWidth()/2f,y=getHeight()/2f,r=Math.min(x,y)-dp(5);p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(dp(3));p.setColor(Color.rgb(224,228,220));c.drawCircle(x,y,r,p);p.setColor(GREEN);c.drawArc(x-r,y-r,x+r,y+r,-90,progress*3.6f,false,p);p.setStyle(Paint.Style.FILL);p.setTextAlign(Paint.Align.CENTER);p.setTypeface(Typeface.DEFAULT_BOLD);p.setTextSize(dp(10));p.setColor(TEXT);c.drawText(label,x,y+dp(4),p);}}
    class TrendView extends View{Paint p=new Paint(1);TrendView(Context c){super(c);}protected void onDraw(Canvas c){float w=getWidth(),h=getHeight();p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(dp(1));p.setColor(Color.rgb(226,230,223));for(int i=1;i<4;i++)c.drawLine(0,h*i/4,w,h*i/4,p);float[] yy={.78f,.67f,.61f,.52f,.56f,.42f,.45f,.32f,.29f,.16f};Path path=new Path();p.setStrokeWidth(dp(2));p.setColor(GREEN);for(int i=0;i<yy.length;i++){float x=dp(2)+(w-dp(4))*i/(yy.length-1),y=h*yy[i];if(i==0)path.moveTo(x,y);else path.lineTo(x,y);}c.drawPath(path,p);}}
    class NavIcon extends View{Paint p=new Paint(1);int type;boolean active;NavIcon(Context c,int t){super(c);type=t;}protected void onDraw(Canvas c){p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(dp(1));p.setStrokeCap(Paint.Cap.ROUND);p.setStrokeJoin(Paint.Join.ROUND);p.setColor(active?GREEN:MUTED);float w=getWidth(),h=getHeight();Path q=new Path();if(type==0){q.moveTo(w*.2f,h*.48f);q.lineTo(w*.5f,h*.2f);q.lineTo(w*.8f,h*.48f);q.moveTo(w*.3f,h*.42f);q.lineTo(w*.3f,h*.78f);q.lineTo(w*.7f,h*.78f);q.lineTo(w*.7f,h*.42f);}else if(type==1){q.moveTo(w*.18f,h*.75f);q.lineTo(w*.36f,h*.57f);q.lineTo(w*.52f,h*.64f);q.lineTo(w*.78f,h*.28f);q.moveTo(w*.69f,h*.28f);q.lineTo(w*.78f,h*.28f);q.lineTo(w*.78f,h*.38f);}else if(type==2){q.moveTo(w*.2f,h*.55f);q.lineTo(w*.42f,h*.74f);q.lineTo(w*.8f,h*.28f);}else{c.drawCircle(w*.5f,h*.35f,w*.15f,p);q.moveTo(w*.24f,h*.78f);q.quadTo(w*.5f,h*.55f,w*.76f,h*.78f);}c.drawPath(q,p);}}
}
