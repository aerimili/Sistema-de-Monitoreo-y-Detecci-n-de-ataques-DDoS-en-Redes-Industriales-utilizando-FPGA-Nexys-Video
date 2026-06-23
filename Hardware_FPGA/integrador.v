`timescale 1ns / 1ps

module integrador(

    input clk,
    input rx,
    input btn_reset,
    
    output tx,
    output led_uart,
    output led_alerta
);

wire alerta;
wire [7:0] datos;
wire datos_validos;
wire [15:0] C1, C2, C3;
wire [15:0] C1n, C2n, C3n;
wire [15:0] valor_nahid;
wire [15:0] th;
wire vector_listo;
wire pulso_reset;

reg btn_s0 = 0;
reg btn_s1 = 0;
reg btn_anterior = 0;
reg [4:0] delay = 0;
reg alerta_limpia = 0;
reg actividad_uart = 0;


always @(posedge clk) begin
    btn_s0 <= btn_reset;
    btn_s1 <= btn_s0;
end

always @(posedge clk) begin
    btn_anterior <= btn_s1;
end

assign pulso_reset = btn_s1 && !btn_anterior;


uart_rx rx_uart (
    .clk(clk),
    .rx(rx),
    .datos(datos),
    .datos_validos(datos_validos)
);


parser_ab parser (
    .clk(clk),
    .datos(datos),
    .datos_validos(datos_validos),
    .C1(C1),
    .C2(C2),
    .C3(C3),
    .C1n(C1n),
    .C2n(C2n),
    .C3n(C3n),
    .th(th),
    .vector_listo(vector_listo)
);


nahid detector (
    .C1(C1),
    .C2(C2),
    .C3(C3),
    .C1n(C1n),
    .C2n(C2n),
    .C3n(C3n),
    .th(th),
    .valor_nahid(valor_nahid),
    .alerta(alerta)
);


always @(posedge clk) begin
    delay <= {delay[3:0], vector_listo};
    if (delay[4]) begin
        alerta_limpia <= alerta;
    end else begin
        alerta_limpia <= 1'b0;
    end
end

ddos_message msg (
    .clk(clk),
    .alerta(alerta_limpia),
    .tx(tx)
);


always @(posedge clk) begin
    if (datos_validos)
        actividad_uart <= ~actividad_uart;
end

assign led_uart = actividad_uart;
assign led_alerta = alerta;


ila_0 ila_inst (
    .clk(clk),
    .probe0(C1),
    .probe1(C2),
    .probe2(C3),
    .probe3(C1n),
    .probe4(C2n),
    .probe5(C3n),
    .probe6(th),
    .probe7(valor_nahid),
    .probe8(alerta),
    .probe9(btn_s1)
);

endmodule