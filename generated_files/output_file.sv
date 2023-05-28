[9:0] adder_instance_1_d;

adder #(
) adder_instance_1 (
    .d( adder_instance_1_d )
    );


multiplier #(
) multiplier_instance (
    .ac( adder_instance_1_d )
    );


multiplier #(
) multiplier_instance_1 (
    .ac( adder_instance_1_d )
    );

