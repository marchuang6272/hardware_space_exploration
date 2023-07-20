`timescale 1ns / 1ps

module top_module_tb;

  // Declare the inputs and outputs of the module
  logic [7:0] a, c, b;
  logic [7:0] test_run, product, test;

  // Instantiate the module under test
  top_module dut (
    .a(a),
    .c(c),
    .b(b),
    .test_run(test_run),
    .product(product),
    .test(test)
  );

  // Test bench logic
  initial begin
    // Initialize signals
    a = 8'b00000000;
    c = 8'b00000000;
    b = 8'b00000000;

    // Drive inputs with values ranging from 0 to 50
    for (int i = 0; i <= 50; i++) begin
      #10;
      a = i;
      #10;
      c = i;
      #10;
      b = i;
    end

    // End simulation
    $finish;
  end

endmodule
