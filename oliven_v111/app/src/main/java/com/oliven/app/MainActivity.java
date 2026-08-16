package com.oliven.app;

import android.app.*;
import android.os.*;
import android.content.*;
import android.graphics.*;
import android.view.*;
import android.widget.*;
import android.text.InputType;
import java.text.*;
import java.util.*;

public class MainActivity extends Activity {
    OlivenView view;

    @Override public void onCreate(Bundle b) {
        super.onCreate(b);
        getWindow().setStatusBarColor(Color.rgb(245, 247, 244));
        getWindow().setNavigationBarColor(Color.BLACK);
        if (Build.VERSION.SDK_INT >= 23) {
            getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR);
        }
        view = new OlivenView(this);
        setContentView(view);
    }

    static class Habit {
        int id;
        String name, goal, cat;
        Habit(int id, String name, String goal, String cat) {
            this.id = id; this.name = name; this.goal = goal; this.cat = cat;
        }
    }

    static class Hit {
        RectF r;
        int type, index;
        Hit(float l, float t, float rr, float b, int type, int index) {
            r = new RectF(l, t, rr, b);
            this.type = type;
            this.index = index;
        }
    }

    static class OlivenView extends View {
        final int BG = Color.rgb(245, 247, 244);
        final int WHITE = Color.WHITE;
        final int TEXT = Color.rgb(21, 29, 24);
        final int MUTED = Color.rgb(104, 114, 108);
        final int GREEN = Color.rgb(31, 111, 78);
        final int GREEN_DARK = Color.rgb(24, 93, 67);
        final int GREEN_SOFT = Color.rgb(230, 246, 239);
        final int OLIVE = Color.rgb(116, 138, 53);
        final int BORDER = Color.rgb(219, 226, 219);
        final int LINE = Color.rgb(235, 239, 234);
        final int CARD_SOFT = Color.rgb(238, 246, 240);
        final Paint p = new Paint(Paint.ANTI_ALIAS_FLAG);
        final ArrayList<Habit> habits = new ArrayList<>();
        final ArrayList<Hit> hits = new ArrayList<>();
        final SharedPreferences prefs;
        final String[] cats = {"Todos", "Corpo", "Mente", "Projetos", "Pessoal"};
        final String[] periods = {"7 dias", "30 dias", "90 dias", "1 ano"};
        Calendar today = Calendar.getInstance();
        Calendar shownMonth = Calendar.getInstance();
        int screen = 0;
        int selectedCat = 0;
        int selectedPeriod = 1;
        boolean menuOpen = false;
        float s = 1f, W = 390f, H = 840f, topH = 72f, bottomH = 92f, contentTop = 72f, contentBottom = 748f;

        OlivenView(Context ctx) {
            super(ctx);
            setLayerType(View.LAYER_TYPE_SOFTWARE, null);
            prefs = ctx.getSharedPreferences("oliven", Context.MODE_PRIVATE);
            shownMonth.set(Calendar.DAY_OF_MONTH, 1);
            shownMonth.set(Calendar.HOUR_OF_DAY, 12);
            shownMonth.set(Calendar.MINUTE, 0);
            loadHabits();
            setFocusable(true);
        }

        void loadHabits() {
            habits.clear();
            String raw = prefs.getString("habits_v2", null);
            if (raw == null || raw.trim().isEmpty()) {
                habits.add(new Habit(1, "Academia", "5x por semana", "Corpo"));
                habits.add(new Habit(2, "Projeto Homem de Ferro", "1h42 / 2h", "Projetos"));
                habits.add(new Habit(3, "Beber água", "3,2 / 3 litros", "Corpo"));
                habits.add(new Habit(4, "Leitura", "30 min por dia", "Mente"));
                habits.add(new Habit(5, "Organização", "Diário", "Pessoal"));
                habits.add(new Habit(6, "Cardio", "4x por semana", "Corpo"));
                habits.add(new Habit(7, "Estudo", "1h por dia", "Mente"));
                saveHabits();
                return;
            }
            for (String line : raw.split("\\n")) {
                if (line.trim().isEmpty()) continue;
                String[] a = line.split("\\t", 4);
                if (a.length == 4) {
                    try { habits.add(new Habit(Integer.parseInt(a[0]), a[1], a[2], a[3])); } catch (Exception ignored) {}
                }
            }
            if (habits.isEmpty()) {
                prefs.edit().remove("habits_v2").apply();
                loadHabits();
            }
        }

        void saveHabits() {
            StringBuilder sb = new StringBuilder();
            for (Habit h : habits) {
                sb.append(h.id).append('\t').append(h.name).append('\t').append(h.goal).append('\t').append(h.cat).append('\n');
            }
            prefs.edit().putString("habits_v2", sb.toString()).apply();
        }

        float X(float v) { return v * s; }
        float Y(float v) { return v * s; }
        Calendar day(int y, int m, int d) { Calendar c = Calendar.getInstance(); c.set(y, m, d, 12, 0, 0); c.set(Calendar.MILLISECOND, 0); return c; }
        String dayKey(Calendar c, int id) { return "done_" + new SimpleDateFormat("yyyyMMdd", Locale.US).format(c.getTime()) + "_" + id; }
        String touchedKey(Calendar c) { return "touched_" + new SimpleDateFormat("yyyyMMdd", Locale.US).format(c.getTime()); }
        int mainCount() { return Math.min(5, habits.size()); }
        boolean done(Calendar c, int i) { return i >= 0 && i < habits.size() && prefs.getBoolean(dayKey(c, habits.get(i).id), false); }
        int doneCount(Calendar c) { int d = 0; for (int i = 0; i < mainCount(); i++) if (done(c, i)) d++; return d; }
        int pct(Calendar c) { return mainCount() == 0 ? 0 : Math.round(doneCount(c) * 100f / mainCount()); }
        boolean sameMonth(Calendar a, Calendar b) { return a.get(Calendar.YEAR) == b.get(Calendar.YEAR) && a.get(Calendar.MONTH) == b.get(Calendar.MONTH); }
        boolean hasData(Calendar c) {
            if (prefs.getBoolean(touchedKey(c), false)) return true;
            for (int i = 0; i < habits.size(); i++) if (done(c, i)) return true;
            return false;
        }
        int monthPct(Calendar base) {
            Calendar m = (Calendar) base.clone();
            m.set(Calendar.DAY_OF_MONTH, 1);
            int max = m.getActualMaximum(Calendar.DAY_OF_MONTH);
            int sum = 0, count = 0;
            for (int d = 1; d <= max; d++) {
                Calendar c = day(m.get(Calendar.YEAR), m.get(Calendar.MONTH), d);
                if (c.after(today)) break;
                if (hasData(c)) { sum += pct(c); count++; }
            }
            return count == 0 ? -1 : Math.round(sum / (float) count);
        }
        int periodPct(int days) {
            Calendar c = (Calendar) today.clone();
            int sum = 0, count = 0;
            for (int i = 0; i < days; i++) {
                if (hasData(c)) { sum += pct(c); count++; }
                c.add(Calendar.DAY_OF_MONTH, -1);
            }
            return count == 0 ? 0 : Math.round(sum / (float) count);
        }
        int periodValue() {
            if (selectedPeriod == 0) return periodPct(7);
            if (selectedPeriod == 1) return periodPct(30);
            if (selectedPeriod == 2) return periodPct(90);
            return periodPct(365);
        }
        int pctColor(int v) {
            if (v <= 0) return Color.TRANSPARENT;
            int alpha = Math.min(235, 42 + v * 2);
            return Color.argb(alpha, 31, 111, 78);
        }
        String monthName(Calendar c) {
            String[] m = {"Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"};
            return m[c.get(Calendar.MONTH)] + " " + c.get(Calendar.YEAR);
        }

        void font(float z, int col, boolean bold) {
            p.setTypeface(Typeface.create("sans", bold ? Typeface.BOLD : Typeface.NORMAL));
            p.setTextSize(X(z));
            p.setColor(col);
            p.setStyle(Paint.Style.FILL);
            p.clearShadowLayer();
        }
        void text(Canvas c, String t, float x, float y, float z, int col, boolean bold) { font(z, col, bold); p.setTextAlign(Paint.Align.LEFT); c.drawText(t, X(x), Y(y), p); }
        void center(Canvas c, String t, float x, float y, float z, int col, boolean bold) { font(z, col, bold); p.setTextAlign(Paint.Align.CENTER); c.drawText(t, X(x), Y(y), p); p.setTextAlign(Paint.Align.LEFT); }
        void right(Canvas c, String t, float x, float y, float z, int col, boolean bold) { font(z, col, bold); p.setTextAlign(Paint.Align.RIGHT); c.drawText(t, X(x), Y(y), p); p.setTextAlign(Paint.Align.LEFT); }
        void round(Canvas c, float l, float t, float r, float b, float rad, int col) { p.setStyle(Paint.Style.FILL); p.setColor(col); p.clearShadowLayer(); c.drawRoundRect(X(l), Y(t), X(r), Y(b), X(rad), X(rad), p); }
        void card(Canvas c, float l, float t, float r, float b, float rad) {
            p.setStyle(Paint.Style.FILL); p.setColor(WHITE); p.setShadowLayer(X(2.5f), 0, X(1.6f), 0x16000000); c.drawRoundRect(X(l), Y(t), X(r), Y(b), X(rad), X(rad), p);
            p.clearShadowLayer(); p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(X(.75f)); p.setColor(BORDER); c.drawRoundRect(X(l), Y(t), X(r), Y(b), X(rad), X(rad), p);
        }
        void line(Canvas c, float x1, float y1, float x2, float y2, int col, float w) { p.setStyle(Paint.Style.STROKE); p.setStrokeCap(Paint.Cap.ROUND); p.setStrokeWidth(X(w)); p.setColor(col); c.drawLine(X(x1), Y(y1), X(x2), Y(y2), p); }
        void check(Canvas c, float x, float y, boolean d) { p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(X(1.2f)); p.setColor(d ? GREEN : MUTED); c.drawCircle(X(x), Y(y), X(5.8f), p); if (d) { p.setStyle(Paint.Style.FILL); p.setColor(GREEN); c.drawCircle(X(x), Y(y), X(4.6f), p); } }

        void olivenLogo(Canvas c, float x, float y, float size, boolean withText) {
            p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(X(size * .075f)); p.setStrokeCap(Paint.Cap.BUTT); p.setColor(OLIVE);
            RectF rr = new RectF(X(x), Y(y), X(x + size), Y(y + size));
            c.drawArc(rr, 200, 140, false, p); c.drawArc(rr, 20, 140, false, p);
            p.setStrokeWidth(X(size * .065f)); p.setStrokeCap(Paint.Cap.ROUND);
            line(c, x + size * .08f, y + size * .50f, x + size * .35f, y + size * .50f, OLIVE, size * .065f);
            line(c, x + size * .65f, y + size * .50f, x + size * .92f, y + size * .50f, OLIVE, size * .065f);
            p.setStyle(Paint.Style.FILL); p.setColor(OLIVE);
            c.drawCircle(X(x + size * .08f), Y(y + size * .50f), X(size * .06f), p);
            c.drawCircle(X(x + size * .35f), Y(y + size * .50f), X(size * .07f), p);
            c.drawCircle(X(x + size * .65f), Y(y + size * .50f), X(size * .07f), p);
            c.drawCircle(X(x + size * .92f), Y(y + size * .50f), X(size * .06f), p);
            if (withText) text(c, "Oliven", x + size + 9, y + size * .68f, 17, TEXT, true);
        }

        @Override protected void onDraw(Canvas c) {
            W = getWidth() / s;
            s = getWidth() / 390f;
            H = getHeight() / s;
            topH = 72f;
            bottomH = 92f;
            contentTop = topH + 16f;
            contentBottom = H - bottomH - 8f;
            hits.clear();
            c.drawColor(BG);
            drawTopbar(c);
            if (screen == 0) drawHome(c);
            else if (screen == 1) drawProgress(c);
            else if (screen == 2) drawHabits(c);
            else if (screen == 3) drawProfile(c);
            else if (screen == 4) drawCalendarCircle(c);
            else drawYearInsights(c);
            drawBottom(c);
            if (menuOpen) drawMenu(c);
        }

        void drawTopbar(Canvas c) {
            round(c, 0, 0, 390, topH, 0, WHITE);
            line(c, 0, topH - .5f, 390, topH - .5f, LINE, .75f);
            round(c, 14, 12, 44, 42, 9, GREEN_SOFT);
            olivenLogo(c, 19, 17, 20, false);
            text(c, screen == 0 ? "Oliven" : title(), 55, 33, 14, TEXT, true);
            topIcon(c, 315, 12, "♢");
            topIcon(c, 350, 12, "☰");
            hits.add(new Hit(X(342), Y(6), X(382), Y(52), 1, 0));
        }
        String title() {
            if (screen == 1) return "Evolução";
            if (screen == 2) return "Hábitos";
            if (screen == 3) return "Perfil";
            if (screen == 4) return "Calendário e Círculo";
            return "Meu ano";
        }
        void topIcon(Canvas c, float x, float y, String sText) { card(c, x, y, x + 28, y + 28, 9); center(c, sText, x + 14, y + 20, 12, TEXT, false); }

        void drawBottom(Canvas c) {
            float y = H - bottomH;
            round(c, 0, y, 390, H, 0, WHITE);
            line(c, 0, y, 390, y, LINE, .8f);
            String[] labels = {"Início", "Progresso", "Hábitos", "Perfil"};
            String[] icons = {"⌂", "↗", "✓", "♙"};
            for (int i = 0; i < 4; i++) {
                float cx = 48 + i * 98;
                boolean act = screen == i || (screen == 4 && i == 0) || (screen == 5 && i == 1);
                if (act) round(c, cx - 44, y + 10, cx + 44, y + 70, 16, GREEN_SOFT);
                center(c, icons[i], cx, y + 32, 19, act ? GREEN : MUTED, true);
                center(c, labels[i], cx, y + 55, 9.5f, act ? GREEN : MUTED, act);
                hits.add(new Hit(X(cx - 48), Y(y), X(cx + 48), Y(H), 2, i));
            }
        }

        void drawHome(Canvas c) {
            text(c, "Olá, Jean.", 18, contentTop + 24, 24, TEXT, true);
            text(c, "16/08/2026 · Evolução pessoal", 18, contentTop + 45, 10.5f, MUTED, false);
            float ringY = contentTop + 155;
            drawSegmentRing(c, 195, ringY, 112, 31, pct(today), false);
            center(c, pct(today) + "%", 195, ringY + 10, 38, TEXT, true);
            center(c, "Consistência de hoje", 195, ringY + 35, 10, MUTED, false);
            hits.add(new Hit(X(70), Y(ringY - 122), X(320), Y(ringY + 122), 8, 4));
            float top = contentTop + 295;
            float b = Math.min(contentBottom - 78, top + 252);
            card(c, 14, top, 376, b, 18);
            text(c, "HOJE", 28, top + 30, 12, TEXT, true);
            right(c, doneCount(today) + " de " + mainCount() + " concluídos", 360, top + 30, 10.8f, GREEN, true);
            float row = (b - top - 52) / Math.max(1, mainCount());
            for (int i = 0; i < mainCount(); i++) {
                float yy = top + 58 + i * row;
                check(c, 38, yy - 5, done(today, i));
                text(c, habits.get(i).name, 56, yy - 9, 12.5f, TEXT, true);
                text(c, habits.get(i).goal, 56, yy + 8, 8.7f, MUTED, false);
                hits.add(new Hit(X(22), Y(yy - row * .45f), X(365), Y(yy + row * .45f), 3, i));
            }
            float iy = b + 14;
            round(c, 14, iy, 376, iy + 58, 17, GREEN_SOFT);
            text(c, "↗", 30, iy + 36, 15, GREEN, true);
            text(c, "Seu ritmo está ficando mais consistente", 58, iy + 28, 12, TEXT, true);
            text(c, "Toque para ver Meu ano e insights", 58, iy + 44, 8.6f, MUTED, false);
            hits.add(new Hit(X(14), Y(iy), X(376), Y(iy + 58), 8, 5));
        }

        void drawProgress(Canvas c) {
            float y = contentTop;
            for (int i = 0; i < periods.length; i++) {
                float l = 16 + i * 89;
                round(c, l, y, l + 82, y + 30, 16, i == selectedPeriod ? GREEN_SOFT : WHITE);
                center(c, periods[i], l + 41, y + 20, 8.8f, i == selectedPeriod ? TEXT : MUTED, i == selectedPeriod);
                hits.add(new Hit(X(l), Y(y), X(l + 82), Y(y + 30), 5, i));
            }
            int pv = periodValue();
            card(c, 14, y + 44, 376, y + 236, 18);
            text(c, "Taxa de consistência", 30, y + 72, 10.5f, MUTED, false);
            text(c, pv + "%", 30, y + 112, 30, TEXT, true);
            text(c, "↑ evolução do seu ritmo", 30, y + 137, 10.2f, GREEN, true);
            for (int i = 0; i < 4; i++) line(c, 32, y + 163 + i * 18, 358, y + 163 + i * 18, BORDER, .55f);
            Path path = new Path();
            for (int i = 0; i < 10; i++) {
                float xx = 32 + i * 36;
                float yy = y + 212 - (i * 10 + (i % 3) * 8);
                if (i == 0) path.moveTo(X(xx), Y(yy)); else path.lineTo(X(xx), Y(yy));
            }
            p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(X(2.3f)); p.setColor(GREEN); p.setStrokeCap(Paint.Cap.ROUND); c.drawPath(path, p);
            card(c, 14, y + 252, 376, y + 380, 18);
            text(c, "Resumo", 30, y + 281, 13, TEXT, true);
            String[] r = {"Hoje", "Semana", "Mês", "Últimos 90 dias"};
            int[] v = {pct(today), periodPct(7), Math.max(0, monthPct(today)), periodPct(90)};
            for (int i = 0; i < 4; i++) { text(c, r[i], 30, y + 310 + i * 20, 9.2f, TEXT, false); right(c, v[i] + "%", 354, y + 310 + i * 20, 9.2f, GREEN, true); }
            card(c, 14, y + 396, 188, y + 470, 16);
            text(c, "Calendário + Círculo", 28, y + 424, 11.5f, TEXT, true); text(c, "Ver mês atual", 28, y + 444, 8.5f, MUTED, false); text(c, "›", 165, y + 438, 18, GREEN, true); hits.add(new Hit(X(14), Y(y + 396), X(188), Y(y + 470), 8, 4));
            card(c, 202, y + 396, 376, y + 470, 16);
            text(c, "Meu ano", 216, y + 424, 11.5f, TEXT, true); text(c, "Insights juntos", 216, y + 444, 8.5f, MUTED, false); text(c, "›", 352, y + 438, 18, GREEN, true); hits.add(new Hit(X(202), Y(y + 396), X(376), Y(y + 470), 8, 5));
        }

        void drawHabits(Canvas c) {
            float y = contentTop;
            text(c, "Meus hábitos", 18, y + 20, 22, TEXT, true);
            text(c, "+", 352, y + 20, 22, TEXT, true);
            hits.add(new Hit(X(332), Y(y - 10), X(382), Y(y + 38), 7, 0));
            y += 42;
            for (int i = 0; i < cats.length; i++) {
                float l = 14 + i * 73;
                round(c, l, y, l + 66, y + 30, 15, i == selectedCat ? GREEN_SOFT : WHITE);
                center(c, cats[i], l + 33, y + 20, 8.5f, i == selectedCat ? GREEN : MUTED, i == selectedCat);
                hits.add(new Hit(X(l), Y(y), X(l + 66), Y(y + 30), 6, i));
            }
            y += 44;
            int drawn = 0;
            for (int i = 0; i < habits.size(); i++) {
                Habit h = habits.get(i);
                if (selectedCat != 0 && !h.cat.equals(cats[selectedCat])) continue;
                float top = y + drawn * 58;
                if (top + 52 > contentBottom) break;
                card(c, 14, top, 376, top + 50, 15);
                round(c, 28, top + 10, 60, top + 42, 10, GREEN_SOFT);
                center(c, iconFor(h), 44, top + 31, 12, GREEN, true);
                text(c, h.name, 74, top + 23, 12.5f, TEXT, true);
                text(c, h.goal, 74, top + 39, 8.5f, MUTED, false);
                text(c, "⋮", 352, top + 32, 16, MUTED, true);
                drawn++;
            }
            if (drawn == 0) center(c, "Nenhum hábito nesta categoria", 195, y + 90, 12, MUTED, false);
        }
        String iconFor(Habit h) {
            if (h.name.toLowerCase(Locale.ROOT).contains("cardio")) return "♥";
            if (h.cat.equals("Mente")) return "▤";
            if (h.cat.equals("Projetos")) return "◆";
            if (h.cat.equals("Pessoal")) return "✓";
            return "●";
        }

        void drawProfile(Canvas c) {
            float y = contentTop;
            card(c, 14, y, 376, y + 72, 16);
            round(c, 30, y + 13, 76, y + 59, 23, GREEN);
            center(c, "J", 53, y + 45, 20, WHITE, true);
            text(c, "Jean Silva", 92, y + 32, 13, TEXT, true);
            text(c, "Membro desde abr/2024", 92, y + 49, 8.2f, MUTED, false);
            y += 88;
            String[][] opts = {{"Dados pessoais", "Nome, preferências e objetivo"}, {"Preferências", "Aparência e rotina"}, {"Notificações", "Lembretes da rotina"}, {"Backup e sincronização", "Em breve"}, {"Ajuda e suporte", "Central de ajuda"}, {"Sobre a Oliven", "Oliven 1.0.11 · Android nativo"}};
            for (int i = 0; i < opts.length; i++) {
                float top = y + i * 58;
                if (top + 50 > contentBottom) break;
                card(c, 14, top, 376, top + 50, 15);
                text(c, opts[i][0], 28, top + 23, 11.5f, TEXT, true);
                text(c, opts[i][1], 28, top + 39, 8.2f, MUTED, false);
                text(c, "›", 352, top + 33, 18, MUTED, true);
            }
        }

        void drawCalendarCircle(Canvas c) {
            float y = contentTop;
            float calH = 178, ringH = 178, habitsH = 188, monthH = 62;
            card(c, 14, y, 376, y + calH, 18);
            text(c, "Calendário", 28, y + 26, 13, TEXT, true);
            center(c, monthName(shownMonth), 195, y + 26, 10.5f, TEXT, true);
            text(c, "‹", 34, y + 29, 18, TEXT, true); text(c, "›", 350, y + 29, 18, TEXT, true);
            hits.add(new Hit(X(22), Y(y + 2), X(65), Y(y + 44), 10, -1));
            hits.add(new Hit(X(325), Y(y + 2), X(368), Y(y + 44), 10, 1));
            drawCalendarGrid(c, 30, y + 48, 360, y + calH - 14, shownMonth);
            y += calH + 10;
            card(c, 14, y, 376, y + ringH, 18);
            center(c, "Círculo de consistência", 195, y + 26, 12, TEXT, true);
            drawMonthlyRing(c, 195, y + 100, 70, shownMonth);
            y += ringH + 10;
            card(c, 14, y, 376, y + habitsH, 18);
            text(c, shownMonth.get(Calendar.DAY_OF_MONTH) == 1 && sameMonth(shownMonth, today) ? "Hábitos de hoje" : "Hábitos do dia", 28, y + 26, 12.5f, TEXT, true);
            right(c, doneCount(today) + " de " + mainCount(), 354, y + 26, 10, GREEN, true);
            float row = 27f;
            for (int i = 0; i < mainCount(); i++) {
                float yy = y + 55 + i * row;
                check(c, 36, yy - 4, done(today, i));
                text(c, habits.get(i).name, 56, yy - 7, 10.8f, TEXT, true);
                text(c, habits.get(i).goal, 56, yy + 8, 7.8f, MUTED, false);
                hits.add(new Hit(X(24), Y(yy - 14), X(360), Y(yy + 12), 3, i));
            }
            y += habitsH + 10;
            card(c, 14, y, 376, y + monthH, 18);
            int mp = monthPct(shownMonth);
            text(c, mp < 0 ? "-" : mp + "%", 28, y + 39, 24, GREEN, true);
            text(c, "Consistência do mês", 100, y + 29, 10.5f, TEXT, false);
            text(c, "Baseada nos registros reais", 100, y + 45, 8.3f, MUTED, false);
        }

        void drawCalendarGrid(Canvas c, float l, float t, float r, float b, Calendar month) {
            String[] week = {"D", "S", "T", "Q", "Q", "S", "S"};
            float col = (r - l) / 7f;
            float row = (b - t) / 6f;
            for (int i = 0; i < 7; i++) center(c, week[i], l + col * i + col / 2, t + 10, 8, MUTED, true);
            Calendar first = (Calendar) month.clone(); first.set(Calendar.DAY_OF_MONTH, 1);
            int start = first.get(Calendar.DAY_OF_WEEK) - 1;
            int max = first.getActualMaximum(Calendar.DAY_OF_MONTH);
            for (int d = 1; d <= max; d++) {
                int idx = start + d - 1, cc = idx % 7, rr = idx / 7;
                float cx = l + col * cc + col / 2, cy = t + 28 + row * rr;
                Calendar cur = day(first.get(Calendar.YEAR), first.get(Calendar.MONTH), d);
                int pc = cur.after(today) ? 0 : pct(cur);
                if (!cur.after(today) && pc > 0) round(c, cx - 12, cy - 12, cx + 12, cy + 12, 12, pctColor(pc));
                if (cur.get(Calendar.YEAR) == today.get(Calendar.YEAR) && cur.get(Calendar.MONTH) == today.get(Calendar.MONTH) && cur.get(Calendar.DAY_OF_MONTH) == today.get(Calendar.DAY_OF_MONTH)) {
                    p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(X(1)); p.setColor(GREEN); c.drawRoundRect(X(cx - 12), Y(cy - 12), X(cx + 12), Y(cy + 12), X(12), X(12), p);
                }
                center(c, String.valueOf(d), cx, cy + 4, 8.5f, pc >= 70 ? WHITE : (pc > 0 ? GREEN : MUTED), pc > 0);
            }
        }

        void drawSegmentRing(Canvas c, float cx, float cy, float radius, int pieces, int percent, boolean proportionalByDay) {
            int active = Math.round(pieces * percent / 100f);
            for (int i = 0; i < pieces; i++) {
                float angle = -90 + i * (360f / pieces);
                c.save(); c.rotate(angle, X(cx), Y(cy));
                float fill = proportionalByDay ? Math.max(0f, Math.min(1f, percent / 100f)) : (i < active ? 1f : 0f);
                float segW = proportionalByDay ? 7.5f : 4.8f;
                float segH = proportionalByDay ? 19f : 16f;
                round(c, cx - segW / 2, cy - radius, cx + segW / 2, cy - radius + segH, 3, LINE);
                if (fill > 0) round(c, cx - segW / 2, cy - radius + segH * (1f - fill), cx + segW / 2, cy - radius + segH, 3, GREEN);
                c.restore();
            }
        }
        void drawMonthlyRing(Canvas c, float cx, float cy, float radius, Calendar month) {
            Calendar first = (Calendar) month.clone(); first.set(Calendar.DAY_OF_MONTH, 1);
            int max = first.getActualMaximum(Calendar.DAY_OF_MONTH);
            for (int d = 1; d <= max; d++) {
                Calendar cur = day(first.get(Calendar.YEAR), first.get(Calendar.MONTH), d);
                float pc = cur.after(today) ? 0 : pct(cur);
                float angle = -90 + (d - 1) * (360f / max);
                c.save(); c.rotate(angle, X(cx), Y(cy));
                round(c, cx - 4.2f, cy - radius, cx + 4.2f, cy - radius + 24, 3, LINE);
                if (pc > 0) round(c, cx - 4.2f, cy - radius + 24 * (1 - pc / 100f), cx + 4.2f, cy - radius + 24, 3, GREEN);
                c.restore();
            }
            center(c, String.valueOf(today.get(Calendar.DAY_OF_MONTH)), cx, cy - 2, 24, TEXT, true);
            center(c, new SimpleDateFormat("MMM", new Locale("pt", "BR")).format(today.getTime()).toUpperCase(Locale.ROOT), cx, cy + 19, 8, MUTED, true);
        }

        void drawYearInsights(Canvas c) {
            float y = contentTop;
            center(c, "Meu ano em 2026", 195, y + 16, 15, TEXT, true);
            y += 36;
            card(c, 14, y, 376, y + 278, 18);
            String[] months = {"JAN", "FEV", "MAR", "ABR", "MAI", "JUN", "JUL", "AGO", "SET", "OUT", "NOV", "DEZ"};
            for (int i = 0; i < 12; i++) {
                int col = i % 4, row = i / 4;
                float cx = 58 + col * 91, cy = y + 58 + row * 76;
                center(c, months[i], cx, cy - 28, 8, MUTED, true);
                Calendar m = day(2026, i, 1);
                int mp = monthPct(m);
                p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(X(2.2f)); p.setColor(mp < 0 ? BORDER : GREEN); c.drawCircle(X(cx), Y(cy), X(24), p);
                center(c, mp < 0 ? "-" : mp + "%", cx, cy + 4, 8.5f, mp < 0 ? MUTED : TEXT, true);
            }
            y += 292;
            card(c, 14, y, 376, contentBottom, 18);
            text(c, "Insights da Oliven", 28, y + 28, 13, TEXT, true);
            float innerTop = y + 42, innerBottom = contentBottom - 12;
            String[][] ins = {{"↗", "Você é mais consistente", "nos dias em que inicia cedo."}, {"◷", "Suas noites após as 21h", "têm menor conclusão."}, {"↗", "Seu desempenho geral", "melhorou com pequenos passos."}};
            for (int i = 0; i < ins.length; i++) {
                float top = innerTop + i * 62;
                if (top + 52 > innerBottom) break;
                round(c, 28, top, 362, top + 52, 13, WHITE);
                text(c, ins[i][0], 42, top + 32, 13, GREEN, true);
                text(c, ins[i][1], 78, top + 23, 10.5f, TEXT, true);
                text(c, ins[i][2], 78, top + 39, 8.2f, MUTED, false);
            }
        }

        void drawMenu(Canvas c) {
            p.setStyle(Paint.Style.FILL); p.setColor(0x88000000); c.drawRect(0, 0, getWidth(), getHeight(), p);
            float l = 18, t = 92, r = 338, b = Math.min(H - bottomH - 12, 506);
            round(c, l, t, r, b, 18, WHITE);
            olivenLogo(c, l + 18, t + 18, 36, true);
            String[] items = {"Tela Inicial", "Evolução", "Hábitos", "Calendário + Círculo", "Meu ano + Insights", "Perfil"};
            int[] targets = {0, 1, 2, 4, 5, 3};
            for (int i = 0; i < items.length; i++) {
                float yy = t + 82 + i * 44;
                text(c, items[i], l + 28, yy, 14, TEXT, false);
                hits.add(new Hit(X(l), Y(yy - 30), X(r), Y(yy + 12), 13, targets[i]));
            }
        }

        @Override public boolean onTouchEvent(android.view.MotionEvent e) {
            if (e.getAction() != MotionEvent.ACTION_UP) return true;
            float x = e.getX(), y = e.getY();
            for (int i = hits.size() - 1; i >= 0; i--) {
                Hit h = hits.get(i);
                if (!h.r.contains(x, y)) continue;
                if (h.type == 1) { menuOpen = !menuOpen; invalidate(); return true; }
                if (h.type == 2) { screen = h.index; menuOpen = false; invalidate(); return true; }
                if (h.type == 3) { toggleHabit(h.index); return true; }
                if (h.type == 5) { selectedPeriod = h.index; invalidate(); return true; }
                if (h.type == 6) { selectedCat = h.index; invalidate(); return true; }
                if (h.type == 7) { showNewHabitDialog(); return true; }
                if (h.type == 8) { screen = h.index; invalidate(); return true; }
                if (h.type == 10) { shownMonth.add(Calendar.MONTH, h.index); invalidate(); return true; }
                if (h.type == 13) { screen = h.index; menuOpen = false; invalidate(); return true; }
            }
            if (menuOpen) { menuOpen = false; invalidate(); return true; }
            return true;
        }
        void toggleHabit(int i) {
            if (i < 0 || i >= habits.size()) return;
            boolean d = done(today, i);
            prefs.edit().putBoolean(dayKey(today, habits.get(i).id), !d).putBoolean(touchedKey(today), true).apply();
            invalidate();
        }
        void showNewHabitDialog() {
            final LinearLayout box = new LinearLayout(getContext());
            box.setOrientation(LinearLayout.VERTICAL);
            int pad = (int) X(18); box.setPadding(pad, pad / 2, pad, 0);
            final EditText nome = new EditText(getContext()); nome.setHint("Nome do hábito"); nome.setSingleLine(true);
            final EditText meta = new EditText(getContext()); meta.setHint("Meta"); meta.setSingleLine(true); meta.setInputType(InputType.TYPE_CLASS_TEXT);
            final EditText cat = new EditText(getContext()); cat.setHint("Categoria: Corpo, Mente, Projetos ou Pessoal"); cat.setSingleLine(true);
            box.addView(nome); box.addView(meta); box.addView(cat);
            new AlertDialog.Builder(getContext())
                .setTitle("Novo hábito")
                .setView(box)
                .setNegativeButton("CANCELAR", null)
                .setPositiveButton("ADICIONAR", (d, w) -> {
                    String n = nome.getText().toString().trim();
                    String m = meta.getText().toString().trim();
                    String ca = cat.getText().toString().trim();
                    if (n.isEmpty()) return;
                    if (m.isEmpty()) m = "Diário";
                    if (!ca.equals("Corpo") && !ca.equals("Mente") && !ca.equals("Projetos") && !ca.equals("Pessoal")) ca = "Pessoal";
                    int next = 1; for (Habit h : habits) next = Math.max(next, h.id + 1);
                    habits.add(new Habit(next, n, m, ca));
                    saveHabits(); invalidate();
                }).show();
        }
    }
}
