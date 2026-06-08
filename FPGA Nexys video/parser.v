`timescale 1ns / 1ps

module parser_ab(

    input clk,
    input [7:0] datos,
    input datos_validos,

    output reg [15:0] C1    = 0,
    output reg [15:0] C2    = 0,
    output reg [15:0] C3    = 0,
    output reg [15:0] C1n   = 0,
    output reg [15:0] C2n   = 0,
    output reg [15:0] C3n   = 0,
    output reg [15:0] th    = 0,
    output reg vector_listo = 0
);

localparam modo_esp = 2'b00;
localparam id_esp   = 2'b01;
localparam leer_num = 2'b10;

reg [1:0] estado = modo_esp;
reg modo         = 0;
reg [7:0] id     = 0;
reg [15:0] valor = 0;
reg [15:0] t1    = 0;
reg [15:0] t2    = 0;
reg [15:0] t3    = 0;
reg [15:0] tn1   = 0;
reg [15:0] tn2   = 0;
reg [15:0] tn3   = 0;


always @(posedge clk) begin
    vector_listo <= 0;
    if (datos_validos) begin
        case(estado)
            modo_esp: begin
                if (datos == "N") begin
                    modo <= 1;
                    estado <= id_esp;
                end

                else if (datos == "D") begin
                    modo <= 0;
                    estado <= id_esp;
                end
            
                else if (datos == 8'h0A || datos == 8'h0D || datos == " ") begin
                    estado <= id_esp;
                end
            
                else begin
                    estado <= id_esp;              
                end
            end

            id_esp: begin
                if (datos == "A" || datos == "B" || datos == "C" || datos == "T") begin
                    id <= datos;
                    valor <= 0;
                    estado <= leer_num;
                end
    
                else begin
                    estado <= modo_esp;
                end
            end
    
            leer_num: begin
                if (datos >= "0" && datos <= "9") begin
                    valor <= (valor * 10) + (datos - "0");
                end
    
                else if (datos == 8'h0A || datos == 8'h0D) begin
                    if (modo) begin
                        case(id)
                            "A":
                                tn1 <= valor;
                            "B":
                                tn2 <= valor;
                            "C": begin
                                tn3 <= valor; 
                                                                        
                                C1n <= tn1;
                                C2n <= tn2;
                                C3n <= valor;
                                vector_listo <= 1;
                            end
                            
                            "T":
                                th <= valor;        
                        endcase
                    end

                    else begin
                        case(id)
                            "A":
                                t1 <= valor;
                            "B":
                                t2 <= valor;
                            "C": begin
                                t3 <= valor;
                                
                                C1 <= t1;
                                C2 <= t2;
                                C3 <= valor;
                        
                                vector_listo <= 1;
                            end
                        endcase
                    end
                    valor <= 0;
                    estado <= modo_esp;
                end
            end
        endcase
    end
end
endmodule