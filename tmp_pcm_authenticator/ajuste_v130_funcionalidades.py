from pathlib import Path

caminho = Path('build_src/PCM_Authenticator/app/src/main/java/br/com/pcm/authenticator/MainActivity.java')
texto = caminho.read_text(encoding='utf-8')

# Estado das abas, preferências e referência ao botão principal.
antigo = '''    private final Handler handler=new Handler(Looper.getMainLooper());
    private final List<Instalacao> instalacoes=new ArrayList<>();
    private RepositorioInstalacoes repositorio; private CofreSeguro cofre; private LinearLayout lista, conteudo; private TextView contador;
    private final Runnable atualizador=new Runnable(){ public void run(){ renderizar(); handler.postDelayed(this,1000); }};'''
novo = '''    private final Handler handler=new Handler(Looper.getMainLooper());
    private final List<Instalacao> instalacoes=new ArrayList<>();
    private RepositorioInstalacoes repositorio; private CofreSeguro cofre; private LinearLayout lista, conteudo, barraNavegacao; private TextView contador; private Button botaoAdicionar;
    private SharedPreferences preferencias; private String abaAtual="instalacoes";
    private final Runnable atualizador=new Runnable(){ public void run(){ if("instalacoes".equals(abaAtual)){ renderizar(); } else if(contador!=null){ contador.setText(String.format(Locale.getDefault(),"%02ds",Totp.segundosRestantes(System.currentTimeMillis()))); } handler.postDelayed(this,1000); }};'''
if antigo not in texto:
    raise SystemExit('Bloco de campos principal não encontrado')
texto = texto.replace(antigo, novo)

antigo = '@Override protected void onCreate(Bundle b){ super.onCreate(b); configurarJanela(); repositorio=new RepositorioInstalacoes(this); cofre=new CofreSeguro(); instalacoes.addAll(repositorio.listar()); construir(); }'
novo = '@Override protected void onCreate(Bundle b){ super.onCreate(b); configurarJanela(); preferencias=getSharedPreferences("pcm_authenticator_config",MODE_PRIVATE); repositorio=new RepositorioInstalacoes(this); cofre=new CofreSeguro(); instalacoes.addAll(repositorio.listar()); construir(); }'
if antigo not in texto:
    raise SystemExit('onCreate não encontrado')
texto = texto.replace(antigo, novo)

# O botão Adicionar precisa poder ser ocultado nas outras abas.
antigo = 'Button add=new Button(this); add.setText("+  Adicionar instalação"); add.setAllCaps(false); add.setTextColor(Color.WHITE); add.setTextSize(13); add.setTypeface(Typeface.DEFAULT,Typeface.BOLD); add.setBackground(bg(VERDE,12)); add.setElevation(dp(2)); add.setOnClickListener(v->cadastro()); LinearLayout.LayoutParams ap=new LinearLayout.LayoutParams(-1,dp(52)); ap.topMargin=dp(8); ap.bottomMargin=dp(8); conteudo.addView(add,ap);'
novo = 'botaoAdicionar=new Button(this); botaoAdicionar.setText("+  Adicionar instalação"); botaoAdicionar.setAllCaps(false); botaoAdicionar.setTextColor(Color.WHITE); botaoAdicionar.setTextSize(13); botaoAdicionar.setTypeface(Typeface.DEFAULT,Typeface.BOLD); botaoAdicionar.setBackground(bg(VERDE,12)); botaoAdicionar.setElevation(dp(2)); botaoAdicionar.setOnClickListener(v->cadastro()); LinearLayout.LayoutParams ap=new LinearLayout.LayoutParams(-1,dp(52)); ap.topMargin=dp(8); ap.bottomMargin=dp(8); conteudo.addView(botaoAdicionar,ap);'
if antigo not in texto:
    raise SystemExit('Botão Adicionar da v1.2.x não encontrado')
texto = texto.replace(antigo, novo)

# Navegação inferior inspirada no padrão do Oficina PCM: ícone separado, maior, área ativa e rótulo legível.
inicio = texto.index('    private void navegacaoInferior(){')
fim = texto.index('    private void renderizar(){', inicio)
navegacao = '''    private void navegacaoInferior(){
        View div=new View(this); div.setBackgroundColor(BORDA); conteudo.addView(div,new LinearLayout.LayoutParams(-1,dp(1)));
        barraNavegacao=new LinearLayout(this); barraNavegacao.setGravity(Gravity.CENTER); barraNavegacao.setPadding(0,dp(4),0,0);
        atualizarBarraNavegacao();
        conteudo.addView(barraNavegacao,new LinearLayout.LayoutParams(-1,dp(74)));
    }

    private LinearLayout itemNav(String icone,String rotulo,String aba){
        boolean ativo=aba.equals(abaAtual);
        LinearLayout item=new LinearLayout(this); item.setOrientation(LinearLayout.VERTICAL); item.setGravity(Gravity.CENTER); item.setPadding(dp(4),dp(5),dp(4),dp(4));
        if(ativo)item.setBackground(bg(SUAVE,18));
        TextView i=txt(icone,24,ativo?TEXTO:SEC,true); i.setGravity(Gravity.CENTER); item.addView(i,new LinearLayout.LayoutParams(-1,dp(31)));
        TextView r=txt(rotulo,11,ativo?TEXTO:SEC,ativo); r.setGravity(Gravity.CENTER); item.addView(r,new LinearLayout.LayoutParams(-1,dp(22)));
        item.setOnClickListener(v->mudarAba(aba));
        return item;
    }

    private void atualizarBarraNavegacao(){
        if(barraNavegacao==null)return;
        barraNavegacao.removeAllViews();
        barraNavegacao.addView(itemNav("⌂","Instalações","instalacoes"),new LinearLayout.LayoutParams(0,dp(66),1));
        barraNavegacao.addView(itemNav("◷","Histórico","historico"),new LinearLayout.LayoutParams(0,dp(66),1));
        barraNavegacao.addView(itemNav("⚙","Configurações","configuracoes"),new LinearLayout.LayoutParams(0,dp(66),1));
        barraNavegacao.addView(itemNav("ⓘ","Sobre","sobre"),new LinearLayout.LayoutParams(0,dp(66),1));
    }

    private void mudarAba(String aba){
        if(aba.equals(abaAtual))return;
        abaAtual=aba;
        if(botaoAdicionar!=null)botaoAdicionar.setVisibility("instalacoes".equals(abaAtual)?View.VISIBLE:View.GONE);
        atualizarBarraNavegacao();
        renderizar();
    }

'''
texto = texto[:inicio] + navegacao + texto[fim:]

# Renderização por aba.
antigo = '''    private void renderizar(){
        if(lista==null)return; lista.removeAllViews(); long agora=System.currentTimeMillis(); int restante=Totp.segundosRestantes(agora); contador.setText(String.format(Locale.getDefault(),"%02ds",restante));
        if(instalacoes.isEmpty()){ vazio(); return; }
        TextView secao=txt(instalacoes.size()==1?"INSTALAÇÃO":"INSTALAÇÕES",11,SEC,true); secao.setLetterSpacing(.08f); LinearLayout.LayoutParams s=new LinearLayout.LayoutParams(-1,-2); s.bottomMargin=dp(10); lista.addView(secao,s);
        for(int i=0;i<instalacoes.size();i++) card(instalacoes.get(i),i,agora,restante);
    }'''
novo = '''    private void renderizar(){
        if(lista==null)return; lista.removeAllViews(); long agora=System.currentTimeMillis(); int restante=Totp.segundosRestantes(agora); contador.setText(String.format(Locale.getDefault(),"%02ds",restante));
        if("historico".equals(abaAtual)){ renderizarHistorico(); return; }
        if("configuracoes".equals(abaAtual)){ renderizarConfiguracoes(); return; }
        if("sobre".equals(abaAtual)){ renderizarSobre(); return; }
        if(instalacoes.isEmpty()){ vazio(); return; }
        TextView secao=txt(instalacoes.size()==1?"INSTALAÇÃO":"INSTALAÇÕES",11,SEC,true); secao.setLetterSpacing(.08f); LinearLayout.LayoutParams s=new LinearLayout.LayoutParams(-1,-2); s.bottomMargin=dp(10); lista.addView(secao,s);
        for(int i=0;i<instalacoes.size();i++) card(instalacoes.get(i),i,agora,restante);
    }'''
if antigo not in texto:
    raise SystemExit('renderizar() não encontrado')
texto = texto.replace(antigo, novo)

# Registrar o nome da instalação quando o código for copiado.
texto = texto.replace('copiar.setOnClickListener(v->copiar(cf));', 'copiar.setOnClickListener(v->copiar(cf,ins));')

antigo = 'private void copiar(String codigo){ ((ClipboardManager)getSystemService(CLIPBOARD_SERVICE)).setPrimaryClip(ClipData.newPlainText("Código PCM",codigo)); Toast.makeText(this,"Código copiado",Toast.LENGTH_SHORT).show(); }'
novo = '''private void copiar(String codigo,Instalacao ins){
        if(preferencias!=null&&!preferencias.getBoolean("permitir_copia",true)){ Toast.makeText(this,"A cópia de códigos está desativada nas Configurações",Toast.LENGTH_SHORT).show(); return; }
        ((ClipboardManager)getSystemService(CLIPBOARD_SERVICE)).setPrimaryClip(ClipData.newPlainText("Código PCM",codigo));
        registrarHistorico("Código copiado",ins.nome+" · "+ins.identificador);
        Toast.makeText(this,"Código copiado",Toast.LENGTH_SHORT).show();
    }'''
if antigo not in texto:
    raise SystemExit('Método copiar não encontrado')
texto = texto.replace(antigo, novo)

# Histórico de cadastro.
antigo = 'instalacoes.add(new Instalacao(n,i,cofre.criptografar(s),r)); repositorio.salvar(instalacoes); d.dismiss(); renderizar();'
novo = 'instalacoes.add(new Instalacao(n,i,cofre.criptografar(s),r)); repositorio.salvar(instalacoes); registrarHistorico("Instalação adicionada",n+" · "+i); d.dismiss(); renderizar();'
if antigo not in texto:
    raise SystemExit('Persistência do cadastro não encontrada')
texto = texto.replace(antigo, novo)

# Histórico de remoção.
antigo = 'setPositiveButton("Remover",(x,w)->{instalacoes.remove(pos);repositorio.salvar(instalacoes);renderizar();})'
novo = 'setPositiveButton("Remover",(x,w)->{instalacoes.remove(pos);repositorio.salvar(instalacoes);registrarHistorico("Instalação removida",alvo.nome+" · "+alvo.identificador);renderizar();})'
if antigo not in texto:
    raise SystemExit('Ação de remoção não encontrada')
texto = texto.replace(antigo, novo)

# Novas telas e utilitários, inseridos antes de excluir().
marcador = '    private void excluir(int pos){'
if marcador not in texto:
    raise SystemExit('Ponto de inserção antes de excluir() não encontrado')
metodos = r'''    private void tituloTela(String titulo,String descricao){
        TextView t=txt(titulo,22,TEXTO,true); LinearLayout.LayoutParams tp=new LinearLayout.LayoutParams(-1,-2); tp.topMargin=dp(4); lista.addView(t,tp);
        TextView d=txt(descricao,13,SEC,false); d.setLineSpacing(dp(2),1f); LinearLayout.LayoutParams dpv=new LinearLayout.LayoutParams(-1,-2); dpv.topMargin=dp(6); dpv.bottomMargin=dp(18); lista.addView(d,dpv);
    }

    private LinearLayout cardBase(){
        LinearLayout c=new LinearLayout(this); c.setOrientation(LinearLayout.VERTICAL); c.setPadding(dp(18),dp(17),dp(18),dp(17)); c.setBackground(borda(CARD,18,BORDA)); c.setElevation(dp(1)); return c;
    }

    private void registrarHistorico(String tipo,String detalhe){
        if(preferencias==null||!preferencias.getBoolean("registrar_historico",true))return;
        String data=new SimpleDateFormat("dd/MM/yyyy HH:mm",Locale.getDefault()).format(new Date());
        String limpo=(detalhe==null?"":detalhe).replace("|","-").replace("\n"," ");
        String registro=data+"|"+tipo+"|"+limpo;
        String atual=preferencias.getString("historico_local","");
        String novo=registro+(atual==null||atual.isEmpty()?"":"\n"+atual);
        String[] linhas=novo.split("\n");
        if(linhas.length>100){ StringBuilder b=new StringBuilder(); for(int i=0;i<100;i++){ if(i>0)b.append('\n'); b.append(linhas[i]); } novo=b.toString(); }
        preferencias.edit().putString("historico_local",novo).apply();
    }

    private void renderizarHistorico(){
        tituloTela("Histórico","Ações registradas localmente neste aparelho. Códigos e segredos nunca são gravados no histórico.");
        String dados=preferencias.getString("historico_local","");
        if(dados==null||dados.trim().isEmpty()){
            LinearLayout vazio=cardBase(); vazio.setGravity(Gravity.CENTER); vazio.setPadding(dp(24),dp(38),dp(24),dp(38));
            TextView ic=txt("◷",32,TEXTO,false); ic.setGravity(Gravity.CENTER); vazio.addView(ic,new LinearLayout.LayoutParams(-1,dp(42)));
            TextView tt=txt("Nenhuma atividade registrada",17,TEXTO,true); tt.setGravity(Gravity.CENTER); LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-1,-2); p.topMargin=dp(10); vazio.addView(tt,p);
            TextView dd=txt("As próximas inclusões, cópias e remoções aparecerão aqui.",12,SEC,false); dd.setGravity(Gravity.CENTER); dd.setLineSpacing(dp(2),1f); LinearLayout.LayoutParams q=new LinearLayout.LayoutParams(-1,-2); q.topMargin=dp(7); vazio.addView(dd,q); lista.addView(vazio); return;
        }
        String[] eventos=dados.split("\n");
        for(String evento:eventos){
            String[] p=evento.split("\\|",3); if(p.length<2)continue;
            LinearLayout c=cardBase();
            LinearLayout linha=new LinearLayout(this); linha.setGravity(Gravity.TOP);
            TextView ic=txt("◷",20,TEXTO,false); ic.setGravity(Gravity.CENTER); ic.setBackground(bg(SUAVE,20)); linha.addView(ic,new LinearLayout.LayoutParams(dp(42),dp(42)));
            LinearLayout info=new LinearLayout(this); info.setOrientation(LinearLayout.VERTICAL); LinearLayout.LayoutParams ip=new LinearLayout.LayoutParams(0,-2,1); ip.leftMargin=dp(12); linha.addView(info,ip);
            info.addView(txt(p[1],14,TEXTO,true)); if(p.length==3&&!p[2].isEmpty()){ TextView det=txt(p[2],12,SEC,false); LinearLayout.LayoutParams d=new LinearLayout.LayoutParams(-1,-2); d.topMargin=dp(4); info.addView(det,d); }
            TextView data=txt(p[0],10,SEC,false); LinearLayout.LayoutParams dt=new LinearLayout.LayoutParams(-1,-2); dt.topMargin=dp(6); info.addView(data,dt); c.addView(linha);
            LinearLayout.LayoutParams cp=new LinearLayout.LayoutParams(-1,-2); cp.bottomMargin=dp(10); lista.addView(c,cp);
        }
        Button limpar=botao("Limpar histórico",ERRO); limpar.setBackground(borda(CARD,12,ERRO)); limpar.setOnClickListener(v->confirmarLimpezaHistorico()); LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,dp(50)); lp.topMargin=dp(4); lp.bottomMargin=dp(12); lista.addView(limpar,lp);
    }

    private void confirmarLimpezaHistorico(){
        AlertDialog d=new AlertDialog.Builder(this).setTitle("Limpar histórico").setMessage("Deseja apagar o histórico armazenado neste aparelho?").setNegativeButton("Cancelar",null).setPositiveButton("Limpar",(x,w)->{preferencias.edit().remove("historico_local").apply();renderizar();}).create();
        d.setOnShowListener(v->{d.getButton(AlertDialog.BUTTON_POSITIVE).setTextColor(ERRO);d.getButton(AlertDialog.BUTTON_NEGATIVE).setTextColor(TEXTO);}); d.show();
    }

    private void renderizarConfiguracoes(){
        tituloTela("Configurações","Controle o comportamento local do PCM Authenticator e consulte os parâmetros de segurança.");
        LinearLayout seguranca=cardBase(); seguranca.addView(txt("SEGURANÇA E PRIVACIDADE",11,SEC,true));
        adicionarSwitch(seguranca,"Permitir copiar códigos","Autoriza copiar o TOTP atual para a área de transferência.","permitir_copia",true);
        adicionarSwitch(seguranca,"Registrar ações no histórico","Registra inclusões, cópias e remoções sem armazenar códigos ou segredos.","registrar_historico",true);
        lista.addView(seguranca,new LinearLayout.LayoutParams(-1,-2));

        LinearLayout sistema=cardBase(); LinearLayout.LayoutParams sp=new LinearLayout.LayoutParams(-1,-2); sp.topMargin=dp(12); lista.addView(sistema,sp);
        sistema.addView(txt("PARÂMETROS DO AUTENTICADOR",11,SEC,true));
        linhaConfiguracao(sistema,"Janela TOTP","60 segundos");
        linhaConfiguracao(sistema,"Formato do código","6 dígitos");
        linhaConfiguracao(sistema,"Funcionamento","Offline");
        linhaConfiguracao(sistema,"Proteção dos segredos","Android Keystore");
        linhaConfiguracao(sistema,"Instalações cadastradas",String.valueOf(instalacoes.size()));
    }

    private void adicionarSwitch(LinearLayout pai,String titulo,String descricao,String chave,boolean padrao){
        LinearLayout linha=new LinearLayout(this); linha.setGravity(Gravity.CENTER_VERTICAL); linha.setPadding(0,dp(15),0,dp(15));
        LinearLayout textos=new LinearLayout(this); textos.setOrientation(LinearLayout.VERTICAL); linha.addView(textos,new LinearLayout.LayoutParams(0,-2,1));
        textos.addView(txt(titulo,14,TEXTO,true)); TextView d=txt(descricao,11,SEC,false); d.setLineSpacing(dp(2),1f); LinearLayout.LayoutParams dpv=new LinearLayout.LayoutParams(-1,-2); dpv.topMargin=dp(4); textos.addView(d,dpv);
        Switch s=new Switch(this); s.setChecked(preferencias.getBoolean(chave,padrao)); s.setOnCheckedChangeListener((b,marcado)->preferencias.edit().putBoolean(chave,marcado).apply()); LinearLayout.LayoutParams sw=new LinearLayout.LayoutParams(dp(54),dp(44)); sw.leftMargin=dp(10); linha.addView(s,sw);
        pai.addView(linha); View div=new View(this); div.setBackgroundColor(BORDA); pai.addView(div,new LinearLayout.LayoutParams(-1,dp(1)));
    }

    private void linhaConfiguracao(LinearLayout pai,String nome,String valor){
        LinearLayout linha=new LinearLayout(this); linha.setGravity(Gravity.CENTER_VERTICAL); linha.setPadding(0,dp(14),0,dp(14));
        linha.addView(txt(nome,13,TEXTO,false),new LinearLayout.LayoutParams(0,-2,1)); TextView v=txt(valor,12,TEXTO,true); v.setGravity(Gravity.END); linha.addView(v);
        pai.addView(linha); View div=new View(this); div.setBackgroundColor(BORDA); pai.addView(div,new LinearLayout.LayoutParams(-1,dp(1)));
    }

    private void renderizarSobre(){
        tituloTela("Sobre","Informações do aplicativo responsável pelos códigos temporários de autenticação das instalações PCM.");
        LinearLayout destaque=cardBase(); destaque.setGravity(Gravity.CENTER); destaque.setPadding(dp(20),dp(28),dp(20),dp(28));
        TextView ic=txt("⚙",34,TEXTO,true); ic.setGravity(Gravity.CENTER); ic.setBackground(bg(SUAVE,32)); destaque.addView(ic,new LinearLayout.LayoutParams(dp(64),dp(64)));
        TextView nome=txt("PCM Authenticator",20,TEXTO,true); nome.setGravity(Gravity.CENTER); LinearLayout.LayoutParams np=new LinearLayout.LayoutParams(-1,-2); np.topMargin=dp(14); destaque.addView(nome,np);
        TextView ver=txt("Versão "+versaoApp(),12,SEC,false); ver.setGravity(Gravity.CENTER); LinearLayout.LayoutParams vp=new LinearLayout.LayoutParams(-1,-2); vp.topMargin=dp(5); destaque.addView(ver,vp); lista.addView(destaque);

        adicionarCardSobre("⌁","Finalidade","Gera códigos TOTP temporários utilizados na autorização periódica das instalações do Projeto PCM.");
        adicionarCardSobre("⌛","Código temporário","Cada código possui 6 dígitos e é renovado automaticamente a cada 60 segundos.");
        adicionarCardSobre("▣","Funcionamento offline","A geração dos códigos ocorre no próprio aparelho e não depende de conexão com a internet.");
        adicionarCardSobre("▤","Armazenamento protegido","Os segredos das instalações são cifrados e protegidos com recursos do Android Keystore.");
        TextView rodape=txt("Projeto PCM · Autenticação das instalações",11,SEC,false); rodape.setGravity(Gravity.CENTER); LinearLayout.LayoutParams rp=new LinearLayout.LayoutParams(-1,-2); rp.topMargin=dp(18); rp.bottomMargin=dp(12); lista.addView(rodape,rp);
    }

    private void adicionarCardSobre(String icone,String titulo,String descricao){
        LinearLayout c=cardBase(); LinearLayout linha=new LinearLayout(this); linha.setGravity(Gravity.TOP);
        TextView i=txt(icone,22,TEXTO,true); i.setGravity(Gravity.CENTER); i.setBackground(bg(SUAVE,18)); linha.addView(i,new LinearLayout.LayoutParams(dp(44),dp(44)));
        LinearLayout textos=new LinearLayout(this); textos.setOrientation(LinearLayout.VERTICAL); LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(0,-2,1); p.leftMargin=dp(12); linha.addView(textos,p); textos.addView(txt(titulo,14,TEXTO,true)); TextView d=txt(descricao,11,SEC,false); d.setLineSpacing(dp(2),1f); LinearLayout.LayoutParams dpv=new LinearLayout.LayoutParams(-1,-2); dpv.topMargin=dp(5); textos.addView(d,dpv); c.addView(linha);
        LinearLayout.LayoutParams cp=new LinearLayout.LayoutParams(-1,-2); cp.topMargin=dp(10); lista.addView(c,cp);
    }

    private String versaoApp(){
        try{ return getPackageManager().getPackageInfo(getPackageName(),0).versionName; }catch(Exception e){ return "1.3.0"; }
    }

'''
texto = texto.replace(marcador, metodos + marcador)

caminho.write_text(texto, encoding='utf-8')
print('PCM Authenticator v1.3.0: Histórico, Configurações, Sobre e navegação ampliada aplicados')
