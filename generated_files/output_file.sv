[9:0] adder_instance_1_d;
intermediate multiplier_instance_product;
intermediate multiplier_instance_1_product;

adder #(
) adder_instance_1 (
    .d( adder_instance_1_d )
    );


multiplier #(
) multiplier_instance (
    .product( multiplier_instance_product ),
    .ac( adder_instance_1_d ),
    .a( multiplier_instance_1_product )
    );


multiplier #(
) multiplier_instance_1 (
    .product( multiplier_instance_1_product ),
    .ac( adder_instance_1_d ),
    .a( multiplier_instance_product )
    );

