logic  [7:0] adder_instance_1_c_to_multiplier_instance_b;
logic  [9:0] adder_instance_1_d_to_multiplier_instance_ac;
logic  [7:0] adder_instance_1_four_to_multiplier_instance_1_b;
intermediate multiplier_instance_1_product_to_multiplier_instance_a;
adder #(
) adder_instance_1 (
            .four( adder_instance_1_four_to_multiplier_instance_1_b )
);
multiplier #(
) multiplier_instance (
            .a( multiplier_instance_1_product_to_multiplier_instance_a )
);
multiplier #(
) multiplier_instance_1 (
            .product( multiplier_instance_1_product_to_multiplier_instance_a )
);
