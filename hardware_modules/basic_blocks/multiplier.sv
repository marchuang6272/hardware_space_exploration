module multiplier (
  input logic [7:0] a,
  input logic [7:0] cb,
  input logic [7:0] b,
  input logic [7:0] ac,
  input logic [7:0] be,
  input logic [7:0] c,
  input logic clk,
  output logic [7:0] run,
  output logic [7:0] product,
  output logic [7:0] test
);
  logic [7:0] run_reg, product_reg, test_reg;
  always @(posedge clk) begin
    run_reg <= a * b;
    product_reg <= cb * ac;
    test_reg <= be * c;
  end

  assign run = run_reg;
  assign product = product_reg;
  assign test = test_reg;
endmodule
