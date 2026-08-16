package br.com.pcm.authenticator;

import android.app.*;
import android.os.*;
import android.content.*;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.text.InputType;
import android.view.*;
import android.widget.*;
import java.text.SimpleDateFormat;
import java.util.*;

public class MainActivity extends Activity {
    private static final int FUNDO=Color.rgb(249,249,246), CARD=Color.WHITE, VERDE=Color.rgb(20,92,55), VERDE2=Color.rgb(93,157,70), TEXTO=Color.rgb(27,36,31), SEC=Color.rgb(101,111,105), BORDA=Color.rgb(226,230,224), SUAVE=Color.rgb(241,245,239), ALERTA=Color.rgb(183,122,35), ERRO=Color.rgb(177,61,61);
    private final Handler handler=new Handler(Looper.getMainLooper());
    private final List<Instalacao> instalacoes=new ArrayList<>();
    private RepositorioInstalacoes repositorio; private CofreSeguro cofre; private LinearLayout lista, conteudo; private TextView contador;
    private final Runnable atualizador=new Runnable(){ public void run(){ renderizar(); handler.postDelayed(this,1000); }};

    @Override protected void onCreate(Bundle b){ super.onCreate(b); configurarJanela(); repositorio=new RepositorioInstalacoes(this); cofre=new CofreSeguro(); instalacoes.addAll(repositorio.listar()); construir(); }
    @Override protected void onResume(){ super.onResume(); handler.removeCallbacks(atualizador); handler.post(atualizador); }
    @Override protected void onPause(){ super.onPause(); handler.removeCallbacks(atualizador); }

    private void configurarJanela(){ getWindow().setStatusBarColor(FUNDO); getWindow().setNavigationBarColor(FUNDO); getWindow().setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE); getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR|View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR); }
    private int dp(int v){ return Math.round(v*getResources().getDisplayMetrics().density); }
    private TextView txt(String s,int sp,int cor,boolean bold){ TextView t=new TextView(this); t.setText(s); t.setTextSize(sp); t.setTextColor(cor); t.setIncludeFontPadding(false); if(bold)t.setTypeface(Typeface.DEFAULT,Typeface.BOLD); return t; }
    private GradientDrawable bg(int cor,int raio){ GradientDrawable g=new GradientDrawable(); g.setColor(cor); g.setCornerRadius(dp(raio)); return g; }
    private GradientDrawable borda(int cor,int raio,int stroke){ GradientDrawable g=bg(cor,raio); g.setStroke(dp(1),stroke); return g; }

    private void construir(){
        FrameLayout raiz=new FrameLayout(this); raiz.setBackgroundColor(FUNDO);
        conteudo=new LinearLayout(this); conteudo.setOrientation(LinearLayout.VERTICAL); conteudo.setPadding(dp(20),dp(16),dp(20),dp(16)); conteudo.setBackgroundColor(FUNDO); raiz.addView(conteudo,new FrameLayout.LayoutParams(-1,-1));
        raiz.setOnApplyWindowInsetsListener((v,insets)->{ int top,bottom; if(Build.VERSION.SDK_INT>=30){ android.graphics.Insets i=insets.getInsets(WindowInsets.Type.systemBars()); top=i.top; bottom=i.bottom; } else { top=insets.getSystemWindowInsetTop(); bottom=insets.getSystemWindowInsetBottom(); } conteudo.setPadding(dp(20),top+dp(12),dp(20),bottom+dp(16)); return insets; });
        cabecalho();
        ScrollView scroll=new ScrollView(this); scroll.setFillViewport(true); scroll.setOverScrollMode(View.OVER_SCROLL_NEVER); lista=new LinearLayout(this); lista.setOrientation(LinearLayout.VERTICAL); lista.setPadding(0,dp(4),0,dp(18)); scroll.addView(lista); conteudo.addView(scroll,new LinearLayout.LayoutParams(-1,0,1));
        Button add=new Button(this); add.setText("+  Adicionar instalação"); add.setAllCaps(false); add.setTextColor(Color.WHITE); add.setTextSize(13); add.setTypeface(Typeface.DEFAULT,Typeface.BOLD); add.setBackground(bg(VERDE,14)); add.setOnClickListener(v->cadastro()); LinearLayout.LayoutParams ap=new LinearLayout.LayoutParams(-1,dp(54)); ap.topMargin=dp(6); conteudo.addView(add,ap);
        setContentView(raiz); renderizar(); raiz.requestApplyInsets();
    }

    private void cabecalho(){
        LinearLayout linha=new LinearLayout(this); linha.setGravity(Gravity.CENTER_VERTICAL);
        TextView logo=txt("P",18,Color.WHITE,true); logo.setGravity(Gravity.CENTER); logo.setBackground(bg(VERDE,24)); linha.addView(logo,new LinearLayout.LayoutParams(dp(46),dp(46)));
        LinearLayout textos=new LinearLayout(this); textos.setOrientation(LinearLayout.VERTICAL); LinearLayout.LayoutParams tp=new LinearLayout.LayoutParams(0,-2,1); tp.leftMargin=dp(12); linha.addView(textos,tp);
        textos.addView(txt("PCM Authenticator",21,VERDE,true)); TextView sub=txt("Proteção mensal das instalações PCM",12,SEC,false); LinearLayout.LayoutParams sp=new LinearLayout.LayoutParams(-1,-2); sp.topMargin=dp(3); textos.addView(sub,sp);
        contador=txt("",11,VERDE,true); contador.setGravity(Gravity.CENTER); contador.setPadding(dp(11),dp(8),dp(11),dp(8)); contador.setBackground(bg(SUAVE,18)); linha.addView(contador);
        LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,-2); lp.bottomMargin=dp(20); conteudo.addView(linha,lp);
    }

    private void renderizar(){
        if(lista==null)return; lista.removeAllViews(); long agora=System.currentTimeMillis(); int restante=Totp.segundosRestantes(agora); contador.setText(String.format(Locale.getDefault(),"%02ds",restante));
        if(instalacoes.isEmpty()){ vazio(); return; }
        TextView secao=txt(instalacoes.size()==1?"INSTALAÇÃO":"INSTALAÇÕES",11,SEC,true); secao.setLetterSpacing(.08f); LinearLayout.LayoutParams s=new LinearLayout.LayoutParams(-1,-2); s.bottomMargin=dp(10); lista.addView(secao,s);
        for(int i=0;i<instalacoes.size();i++) card(instalacoes.get(i),i,agora,restante);
    }

    private void vazio(){
        LinearLayout v=new LinearLayout(this); v.setOrientation(LinearLayout.VERTICAL); v.setGravity(Gravity.CENTER); v.setPadding(dp(28),dp(42),dp(28),dp(42)); v.setBackground(borda(CARD,20,BORDA)); v.setElevation(dp(1));
        TextView ic=txt("✓",24,VERDE,true); ic.setGravity(Gravity.CENTER); ic.setBackground(bg(SUAVE,30)); v.addView(ic,new LinearLayout.LayoutParams(dp(58),dp(58)));
        TextView t=txt("Nenhuma instalação cadastrada",18,TEXTO,true); t.setGravity(Gravity.CENTER); LinearLayout.LayoutParams tp=new LinearLayout.LayoutParams(-1,-2); tp.topMargin=dp(18); v.addView(t,tp);
        TextView d=txt("Adicione uma instalação PCM para começar a gerar códigos temporários de autenticação.",13,SEC,false); d.setGravity(Gravity.CENTER); d.setLineSpacing(dp(2),1f); LinearLayout.LayoutParams dpv=new LinearLayout.LayoutParams(-1,-2); dpv.topMargin=dp(9); v.addView(d,dpv);
        lista.addView(v); TextView nota=txt("Os segredos ficam protegidos no aparelho pelo Android Keystore.",11,SEC,false); nota.setGravity(Gravity.CENTER); LinearLayout.LayoutParams np=new LinearLayout.LayoutParams(-1,-2); np.topMargin=dp(14); lista.addView(nota,np);
    }

    private void card(Instalacao ins,int idx,long agora,int restante){
        LinearLayout c=new LinearLayout(this); c.setOrientation(LinearLayout.VERTICAL); c.setPadding(dp(18),dp(18),dp(18),dp(16)); c.setBackground(borda(CARD,20,BORDA)); c.setElevation(dp(1));
        LinearLayout cab=new LinearLayout(this); cab.setGravity(Gravity.CENTER_VERTICAL); LinearLayout info=new LinearLayout(this); info.setOrientation(LinearLayout.VERTICAL); cab.addView(info,new LinearLayout.LayoutParams(0,-2,1)); info.addView(txt(ins.nome,18,TEXTO,true)); TextView id=txt(ins.identificador,12,SEC,false); LinearLayout.LayoutParams ip=new LinearLayout.LayoutParams(-1,-2); ip.topMargin=dp(3); info.addView(id,ip);
        String st=status(ins.renovacao); int cs=st.equals("Expirada")?ERRO:st.equals("Renova hoje")?ALERTA:VERDE; TextView chip=txt(st,11,cs,true); chip.setGravity(Gravity.CENTER); chip.setPadding(dp(10),dp(6),dp(10),dp(6)); chip.setBackground(bg(cs==ERRO?Color.rgb(250,239,239):cs==ALERTA?Color.rgb(250,244,232):Color.rgb(237,246,239),16)); cab.addView(chip); c.addView(cab);
        if(!ins.renovacao.isEmpty()){ TextView r=txt("Próxima renovação  •  "+ins.renovacao,12,VERDE,false); LinearLayout.LayoutParams rp=new LinearLayout.LayoutParams(-1,-2); rp.topMargin=dp(12); c.addView(r,rp); }
        View div=new View(this); div.setBackgroundColor(BORDA); LinearLayout.LayoutParams dpv=new LinearLayout.LayoutParams(-1,dp(1)); dpv.topMargin=dp(16); dpv.bottomMargin=dp(16); c.addView(div,dpv);
        String codigo="------"; boolean falha=false; try{ codigo=Totp.gerar(cofre.descriptografar(ins.segredoCriptografado),agora); }catch(Exception e){ codigo="ERRO"; falha=true; }
        TextView rot=txt("CÓDIGO ATUAL",11,SEC,true); rot.setLetterSpacing(.08f); c.addView(rot); TextView cod=txt(formatar(codigo),38,falha?ERRO:VERDE,true); cod.setLetterSpacing(.06f); LinearLayout.LayoutParams cp=new LinearLayout.LayoutParams(-1,-2); cp.topMargin=dp(5); c.addView(cod,cp);
        LinearLayout tempo=new LinearLayout(this); tempo.setGravity(Gravity.CENTER_VERTICAL); tempo.addView(txt(String.format(Locale.getDefault(),"válido por %02d s",restante),12,restante<=10?ALERTA:SEC,false),new LinearLayout.LayoutParams(0,-2,1)); tempo.addView(txt("janela de 60 s",11,SEC,false)); LinearLayout.LayoutParams tl=new LinearLayout.LayoutParams(-1,-2); tl.topMargin=dp(3); c.addView(tempo,tl);
        ProgressBar barra=new ProgressBar(this,null,android.R.attr.progressBarStyleHorizontal); barra.setMax(60); barra.setProgress(restante); barra.setProgressTintList(android.content.res.ColorStateList.valueOf(restante<=10?ALERTA:VERDE2)); barra.setProgressBackgroundTintList(android.content.res.ColorStateList.valueOf(Color.rgb(231,235,230))); LinearLayout.LayoutParams bp=new LinearLayout.LayoutParams(-1,dp(5)); bp.topMargin=dp(10); c.addView(barra,bp);
        LinearLayout acoes=new LinearLayout(this); LinearLayout.LayoutParams al=new LinearLayout.LayoutParams(-1,-2); al.topMargin=dp(14); final String cf=codigo; Button copiar=botao("Copiar código",VERDE); copiar.setOnClickListener(v->copiar(cf)); acoes.addView(copiar,new LinearLayout.LayoutParams(0,dp(46),1)); Button remover=botao("Remover",ERRO); LinearLayout.LayoutParams rp=new LinearLayout.LayoutParams(0,dp(46),1); rp.leftMargin=dp(9); final int pos=idx; remover.setOnClickListener(v->excluir(pos)); acoes.addView(remover,rp); c.addView(acoes,al);
        LinearLayout.LayoutParams out=new LinearLayout.LayoutParams(-1,-2); out.bottomMargin=dp(12); lista.addView(c,out);
    }

    private Button botao(String s,int cor){ Button b=new Button(this); b.setText(s); b.setAllCaps(false); b.setTextSize(12); b.setTextColor(cor); b.setTypeface(Typeface.DEFAULT,Typeface.BOLD); b.setBackground(borda(CARD,12,BORDA)); return b; }
    private String formatar(String c){ return c!=null&&c.length()==6?c.substring(0,3)+"  "+c.substring(3):c; }
    private String status(String r){ if(r==null||r.trim().isEmpty())return "Ativa"; try{ SimpleDateFormat f=new SimpleDateFormat("dd/MM/yyyy",Locale.getDefault()); f.setLenient(false); Date d=f.parse(r.trim()); Calendar a=Calendar.getInstance(), b=Calendar.getInstance(); b.setTime(d); zerar(a); zerar(b); if(b.before(a))return "Expirada"; if(b.equals(a))return "Renova hoje"; }catch(Exception ignored){} return "Ativa"; }
    private void zerar(Calendar c){ c.set(Calendar.HOUR_OF_DAY,0);c.set(Calendar.MINUTE,0);c.set(Calendar.SECOND,0);c.set(Calendar.MILLISECOND,0); }
    private void copiar(String codigo){ ((ClipboardManager)getSystemService(CLIPBOARD_SERVICE)).setPrimaryClip(ClipData.newPlainText("Código PCM",codigo)); Toast.makeText(this,"Código copiado",Toast.LENGTH_SHORT).show(); }

    private EditText campo(String hint){ EditText e=new EditText(this); e.setHint(hint); e.setTextColor(TEXTO); e.setHintTextColor(Color.rgb(145,153,147)); e.setTextSize(14); e.setSingleLine(true); e.setPadding(dp(14),0,dp(14),0); e.setBackground(borda(Color.WHITE,12,BORDA)); return e; }
    private void addCampo(LinearLayout box,String rotulo,EditText campo){ TextView r=txt(rotulo,12,TEXTO,true); LinearLayout.LayoutParams rp=new LinearLayout.LayoutParams(-1,-2); rp.topMargin=dp(14); rp.bottomMargin=dp(7); box.addView(r,rp); box.addView(campo,new LinearLayout.LayoutParams(-1,dp(50))); }

    private void cadastro(){
        Dialog d=new Dialog(this); d.requestWindowFeature(Window.FEATURE_NO_TITLE); ScrollView scroll=new ScrollView(this); LinearLayout box=new LinearLayout(this); box.setOrientation(LinearLayout.VERTICAL); box.setPadding(dp(22),dp(22),dp(22),dp(22)); box.setBackground(bg(CARD,22)); scroll.addView(box); box.addView(txt("Adicionar instalação",21,TEXTO,true)); TextView desc=txt("Cadastre os dados fornecidos no provisionamento do PCM.",13,SEC,false); LinearLayout.LayoutParams dsp=new LinearLayout.LayoutParams(-1,-2); dsp.topMargin=dp(7); box.addView(desc,dsp);
        EditText nome=campo("Ex.: Sorel - Matriz"), id=campo("Ex.: PCM-8F21-74AD"), segredo=campo("Chave Base32"), renovacao=campo("DD/MM/AAAA"); segredo.setInputType(InputType.TYPE_CLASS_TEXT|InputType.TYPE_TEXT_VARIATION_VISIBLE_PASSWORD); renovacao.setInputType(InputType.TYPE_CLASS_DATETIME|InputType.TYPE_DATETIME_VARIATION_DATE); addCampo(box,"Nome da empresa / instalação",nome); addCampo(box,"Identificador",id); addCampo(box,"Segredo Base32",segredo); addCampo(box,"Próxima renovação",renovacao);
        TextView ajuda=txt("O segredo será cifrado e protegido no próprio aparelho.",11,SEC,false); LinearLayout.LayoutParams hp=new LinearLayout.LayoutParams(-1,-2); hp.topMargin=dp(11); box.addView(ajuda,hp);
        LinearLayout acoes=new LinearLayout(this); Button cancelar=botao("Cancelar",SEC); cancelar.setOnClickListener(v->d.dismiss()); acoes.addView(cancelar,new LinearLayout.LayoutParams(0,dp(50),1)); Button salvar=new Button(this); salvar.setText("Salvar instalação"); salvar.setAllCaps(false); salvar.setTextColor(Color.WHITE); salvar.setTypeface(Typeface.DEFAULT,Typeface.BOLD); salvar.setBackground(bg(VERDE,12)); LinearLayout.LayoutParams sl=new LinearLayout.LayoutParams(0,dp(50),1); sl.leftMargin=dp(10); acoes.addView(salvar,sl); LinearLayout.LayoutParams alp=new LinearLayout.LayoutParams(-1,-2); alp.topMargin=dp(20); box.addView(acoes,alp);
        salvar.setOnClickListener(v->{ try{ String n=nome.getText().toString().trim(), i=id.getText().toString().trim(), s=segredo.getText().toString().trim(), r=renovacao.getText().toString().trim(); if(n.isEmpty()||i.isEmpty()||s.isEmpty()){Toast.makeText(this,"Preencha nome, identificador e segredo",Toast.LENGTH_SHORT).show();return;} Totp.decodificarBase32(s); if(!r.isEmpty()){ SimpleDateFormat f=new SimpleDateFormat("dd/MM/yyyy",Locale.getDefault()); f.setLenient(false); f.parse(r); } instalacoes.add(new Instalacao(n,i,cofre.criptografar(s),r)); repositorio.salvar(instalacoes); d.dismiss(); renderizar(); }catch(Exception e){Toast.makeText(this,"Confira o segredo Base32 e a data DD/MM/AAAA",Toast.LENGTH_LONG).show();}});
        d.setContentView(scroll); d.show(); Window w=d.getWindow(); if(w!=null){ w.setBackgroundDrawableResource(android.R.color.transparent); WindowManager.LayoutParams p=w.getAttributes(); p.width=getResources().getDisplayMetrics().widthPixels-dp(32); p.height=WindowManager.LayoutParams.WRAP_CONTENT; p.gravity=Gravity.CENTER; p.dimAmount=.45f; w.addFlags(WindowManager.LayoutParams.FLAG_DIM_BEHIND); w.setAttributes(p); w.setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE); }
    }

    private void excluir(int pos){ if(pos<0||pos>=instalacoes.size())return; Instalacao alvo=instalacoes.get(pos); AlertDialog d=new AlertDialog.Builder(this).setTitle("Remover instalação").setMessage("Deseja remover “"+alvo.nome+"” deste aparelho?").setNegativeButton("Cancelar",null).setPositiveButton("Remover",(x,w)->{instalacoes.remove(pos);repositorio.salvar(instalacoes);renderizar();}).create(); d.setOnShowListener(v->{d.getButton(AlertDialog.BUTTON_POSITIVE).setTextColor(ERRO);d.getButton(AlertDialog.BUTTON_NEGATIVE).setTextColor(VERDE);}); d.show(); }
}
