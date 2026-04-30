`timescale 1ns / 1ps

module parser(
    input clk,
    input [7:0] data,
    input data_valid,

    output reg [15:0] C1 = 0,
    output reg [15:0] C2 = 0,
    output reg [15:0] C3 = 0,
    output reg [15:0] C1n = 0,
    output reg [15:0] C2n = 0,
    output reg [15:0] C3n = 0,
    output reg [15:0] th = 0,

    output reg vector_ready = 0
);

reg [15:0] temp = 0;
reg [3:0] estado = 0;
reg modo = 0; // 1=N, 0=D

always @(posedge clk) begin

    vector_ready <= 0;

    if (data_valid) begin

        if (data == "N") begin
            modo <= 1;
            estado <= 0;
            temp <= 0;
        end

        else if (data == "D") begin
            modo <= 0;
            estado <= 0;
            temp <= 0;
        end

        else if (data >= "0" && data <= "9") begin
            temp <= temp * 10 + (data - "0");
        end

        else if (data == ",") begin
            case (estado)
                0: if (modo) C1n <= temp; else C1 <= temp;
                1: if (modo) C2n <= temp; else C2 <= temp;
                2: if (modo) C3n <= temp; else C3 <= temp;
                3: th <= temp;
            endcase

            temp <= 0;
            estado <= estado + 1;
        end

        else if (data == 8'h0A) begin
            case (estado)
                0: if (modo) C1n <= temp; else C1 <= temp;
                1: if (modo) C2n <= temp; else C2 <= temp;
                2: if (modo) C3n <= temp; else C3 <= temp;
                3: th <= temp;
            endcase

            temp <= 0;
            estado <= 0;

            if (!modo)
                vector_ready <= 1; // 🔥 clave
        end
    end
end

endmodule

// `timescale 1ns / 1ps

//module parser_abc(
//    input clk,
//    input [7:0] data,
//   input data_valid,

//    output reg [15:0] C1 = 0,
//    output reg [15:0] C2 = 0,
//    output reg [15:0] C3 = 0,
//    output reg [15:0] th = 0
//);

//reg [7:0] id = 0;        // A, B, C o T
//reg [15:0] value = 0;

//localparam IDLE = 0;
//localparam READ_NUM = 1;

//reg state = IDLE;

//always @(posedge clk) begin
//    if (data_valid) begin

//        case (state)

        // =========================
        // ESPERANDO ID (A, B, C, T)
        // =========================
//        IDLE: begin
 //           if (data == "A" || data == "B" || data == "C" || data == "T") begin
//                id <= data;
 //               value <= 0;
 //               state <= READ_NUM;
 //           end
 //       end
//
 //       // =========================
 //       // LEYENDO NÚMERO
        // =========================
//        READ_NUM: begin

            // Construcción del número
 //           if (data >= "0" && data <= "9") begin
 //               value <= (value * 10) + (data - "0");
//            end
//
//            // Fin de número
//            else if (data == 8'h0A) begin  // '\n'

//                case (id)
//                    "A": C1 <= value;
//                    "B": C2 <= value;
//                    "C": C3 <= value;
//                    "T": th <= value;
 //               endcase

//                state <= IDLE;
//            end
//        end

//        endcase
//    end
//end

//endmodule

