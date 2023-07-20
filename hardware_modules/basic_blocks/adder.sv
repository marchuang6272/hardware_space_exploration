module adder (
  input logic [7:0] a,
  input logic [7:0] cb,
  input logic [7:0] b,
  input logic [7:0] clk,
  output logic [7:0] run,
  output logic [7:0] c,
  output logic [7:0] d,
  output logic [7:0] four
);
  logic [7:0] run_reg, c_reg, d_reg, four_reg;
  always @(posedge clk) begin
    run_reg <= a + b;
    c_reg <= a + cb;
    d_reg <= b + cb;
    four_reg <= a + b + cb;
  end

  assign run = run_reg;
  assign c = c_reg;
  assign d = d_reg;
  assign four = four_reg;
endmodule
