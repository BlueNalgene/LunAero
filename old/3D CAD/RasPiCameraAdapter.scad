//Diameter of the spotting scope eyepiece in mm.
ssd = 51.6; //[20.001:0.001:150.000]

//This switch sets the quality of the compiled design for printing or just mucking about.
final = 1; //[1:final, 0:draft]

//Select what you want the code to output.
part = 1; //[0:All in one model, 1: Just the RasPi case, 2: Just the camera housing, 3: Just the clamp]

support = 0; //[0: No supports, 1: Supports on clamp]

/*
LunAero Scoped Camera Adapter

This is the adapter for the Raspberry Pi camera to be attached to a spotting scope.
Parametric design is formatted for Thingiverse and MakerBot Customizer format.  Each setting is
    configurable in these programs.  Manual editing of these values can be performed by directly
    editing the OpenSCAD code, where variables are listed above this text.
This design can be configured to produce a single model of the combined part as it should be assembled
    (useful for computer models and sintered 3D printing), or as individual parts which are to be glued
    together (useful for fused filament 3D printing).  This is selected by a drop-down menu type variable.
Supports can be enabled with a drop-down menu type variable.  These supports are rudimentary, and designed to provide only the bare minimum to print successfully without relying on automatic generation of supports by a slicing program (which might mess up parts with tight tolerances.  If you are not confident in these supports, it is recommended to turn them off and generate your own with a slicing program.

Designs by Dr. Wesley Honeycutt in collaboration with Dr. Eli Bridge
*/

//if (final == 0) {
//    $fs = 0.5;
//    $fa = 10;
//}
//else if (final == 1) {
//    $fs = 0.1;
//    $fa = 1;
//}
//else {
//    echo("<font color='red'>Error: The output quality setting has an incorrect value.</font>");
//}

// Global resolution
//$fs = 0.5;  // Don't generate smaller facets than 0.1 mm
//$fa = 10;    // Don't generate larger angles than 5 degrees

// Sanitize ssd input
if (ssd <= 20) {
    echo("<font color='red'>Error: Minimum eyepiece size is 20 mm for this design.</font>")
    assert(false);
}

module raspi() {
    /*
    Measurements borrowed in part from SaarBastler
    See repo for info:
    https://github.com/saarbastler/library.scad
    */
    color("red") {
        union() {
            cube([85,56,1.6], center=true);
            
            //Ethernet Port
            translate([23.5,-24.5,0.8]) cube([21,16,13.8]);
            
            //USB Ports
            translate([27.5,-5.5 ,0.8]) cube([17,13,15.5]);
            translate([27.5,12.5,0.8]) cube([17,13,15.5]);
            
            //micro USB Port
            translate([-35.9,-29.5,0.8]) cube([8,6,2.6]);
            
            //HDMI Port
            translate([-18,-29.5,0.8]) cube([15,11.5,6.6]);
            
            //Phono Jack
            translate([7.5,-28,0.8]) cube([7,13,5.6]);
            translate([11,-28,2.8]) rotate([90,0,0]) cylinder(d=5.6,h=2);
            
            //Display
            translate([-41.4,-14.5,0.8]) cube([4,22,5.5]);
            
            //Camera
            translate([0.5,-26.9,0.8]) cube([4,22,5.5]);
            
            //SD Card
            translate([-42.5,-6,-2.1]) cube([13,14,1.5]);
            translate([-44.9,-4.5,-1.85]) cube([2.4,11,1]);
            
            //Header (SaarBastler design)
            translate([3.5-85/2+29-10*2.54,49/2-2.54,0.8]) cube([50.8,5.08,1.27]);
            translate([3.5-85/2+29-10*2.54,49/2-2.54,0.8]) for(x=[0:19],y=[0:1])
                translate([x*2.54+(1.27+.6)/2,y*2.54+(1.27+.6)/2,-3.5]) cube([0.6,0.6,11.5]);
        }
    }
}

//This module blocks off the top and bottom of the raspi
//for simplification of diff'd void.
module raspiblock() {
    union() {
        raspi();
        translate([0,0,6.5]) cube([85,56,19.5], center = true);
        translate([-50.9,-4.5,-1.85]) cube([12.4,11,18.1]);
    }
}

//This module makes a cube and cuts out a space for the blocked Raspberry Pi.
module body() {
    difference() {
        union() {
            difference() {
                cube([90.4,59,21], center=true);
                translate([2.2,0,-5]) raspiblock();
            }
            //Standoffs are added for the screw holes.
            translate([-35.4,24.5,-8.25]) cylinder(d = 5, h = 2.45);
            translate([-35.4,-24.5,-8.25]) cylinder(d = 5, h = 2.45);
            translate([22.6,24.5,-8.25]) cylinder(d = 5, h = 2.45);
            translate([22.6,-24.5,-8.25]) cylinder(d = 5, h = 2.45);
            //these cubes make the filleted type of standoff
            translate([-37.9,24.5,-8.25]) cube([5,5,2.45]);
            translate([-37.9,-29.5,-8.25]) cube([5,5,2.45]);
            translate([20.1,24.5,-8.25]) cube([5,5,2.45]);
            translate([20.1,-29.5,-8.25]) cube([5,5,2.45]);
            translate([-40.5,22,-8.25]) cube([5,7.5,2.45]);
            translate([-40.5,-29.5,-8.25]) cube([5,7.5,2.45]);
        }
        //These are the drill holes through the body for mounting bolts.
        translate([-35.4,24.5,-19.25]) cylinder(d=2.8, h=30);
        translate([-35.4,-24.5,-19.25]) cylinder(d=2.8, h=30);
        translate([22.6,24.5,-19.25]) cylinder(d=2.8, h=30);
        translate([22.6,-24.5,-19.25]) cylinder(d=2.8, h=30);
        translate([0,0,12]) cube([100,100,10], center = true);
    }
}

//This module provides a design for the Raspberry Pi camera module
//Some measurements taken from larch
//see https://github.com/larsch/openscad-modules/blob/master/rpi-camera.scad
module camera() {
    translate([-14.25,-12.5,0]) union() {
        // PCB
        cube([24,25,1]); 
        // Lens Assembly
        translate([10.25,8.5,1]) cube([8,8,3.25]);
        translate([14.25,12.5,4.25]) cylinder(d=7.5,h=1);
        translate([14.25,12.5,4.95]) cylinder(d=5.5,h=0.7);
        // Upper Lens Assembly
        translate([1.75,8.625,1]) cube([8.5,7.75,1.5]);
        // Flex Cable Mount
        translate([18.25,2.75,-2.75]) cube([4.5,19.5,2.75]);
        translate([22.75,2,-2.75]) cube([1.25,21,2.75]);
        // Flex Cable
        translate([24,4.25,-1]) cube([10,16.5,0.1]); 
    }
}

//This module makes a clamp for the spotting scope.
//This is parametric based on the "ssd" variable in line 2
module clamp() {
    union() {
        // Side 1 of clamp
        rotate(a=5, v=[0,0,ssd/2]) difference() {
            union() {
                // Outer Half-Ring
                translate([0,-ssd/50,0]) cylinder(d = ssd+4, h = 15);
                // Bolt holder
                difference() {
                    translate([-(ssd/2+15),-10,-2]) cube ([15,10,17]);
                    translate([-(ssd/2+15)+5.125,0,7.5]) rotate([90,0,0]) cylinder(d = 3.75, h = 10);
                }
            }
            // Inner Half-Ring 
            translate([0,-ssd/50,0]) cylinder(d = ssd, h = 15);
            translate([-(ssd+4),0,0]) cube([2*ssd+4,ssd/2+4,15]);
        }
        // Side 2 of clamp
        rotate(a=-5, v=[0,0,ssd/2]) difference() {
            union() {
                // Outer Half-Ring 2
                translate([0,ssd/50,0]) cylinder(d = ssd+4, h = 15);
                // Bolt holder 2
                difference() {
                    union() {
                        translate([-(ssd/2+15),2,0]) cube ([15,10,15]);
                        translate([-(ssd/2+15),2,-2]) cube ([12,10,2]);
                    }
                    translate([-(ssd/2+15)+5.125,12,7.5]) rotate([90,0,0]) cylinder(d = 3.75, h = 10);   
                }
            }
        // Inner Half-Ring 2
        translate([0,ssd/50,0]) cylinder(d = ssd, h = 15);
        translate([-(ssd+4)/2,-(ssd+4)/2,0]) cube([ssd+4,ssd/2+4,15]);
        // Cut for Flex
        translate([-(ssd+4)/2,0,0]) cube([ssd+4,ssd/2+4,1]);
        }
        // Camera hole and backing.  The cubes add alignment marks for camera holder.
        rotate(a=5, v=[0,0,ssd/2]) translate([0,-ssd/50,0]) difference() {
            translate([0,0,-2]) cylinder(d = ssd + 4, h = 2);
            translate ([0,0,-5.625]) camera(center=true);
            translate ([14.75,15.25,-1.75]) cube([1.5,0.5,0.5], center = true);
            translate ([15.25,14.75,-1.75]) cube([0.5,1.5,0.5], center = true);
            translate ([-14.75,15.25,-1.75]) cube([1.5,0.5,0.5], center = true);
            translate ([-15.25,14.75,-1.75]) cube([0.5,1.5,0.5], center = true);
            translate ([-14.75,-15.25,-1.75]) cube([1.5,0.5,0.5], center = true);
            translate ([-15.25,-14.75,-1.75]) cube([0.5,1.5,0.5], center = true);
            translate ([14.75,-15.25,-1.75]) cube([1.5,0.5,0.5], center = true);
            translate ([15.25,-14.75,-1.75]) cube([0.5,1.5,0.5], center = true);
        }
        // This places supports on the clamp edge
        if (support > 0) {
            rotate(a=-5, v=[0,0,ssd/2]) difference() {
                translate([0,ssd/50,-2]) cylinder(d = ssd+4, h = 4);
                translate([0,ssd/50,-2]) cylinder(d = ssd, h = 4);
                translate([-(ssd+4)/2,-(ssd+4)/2,-2]) cube([ssd+4,ssd/2+4,4]);
                translate([0,ssd/50,-2]) cylinder(d1 = ssd + 1,d = ssd + 4, h = 4);
                arclength = 2 * PI * ssd * 6;
                spoke = 2*(asin(1 / (2 * ssd)));
                echo("spoke = ",spoke);
            }
        }
    }
}

module cameraholder() {
    // Camera Block, aligns with side 1 of clamp
        union() {
            difference() {
                union() {
                    //%translate([0,0,-2]) cylinder(d = ssd + 4, h = 2);
                    translate([0,0,-3.475]) cube([30,30,3], center = true);
                    difference() {
                        translate([-12.5,0,-6]) cube([5,30,8], center = true);
                        translate([-11.25,0,-6.5]) rotate([0,45,0]) cube([5.5,25,4.5], center = true);
                    }
                }
                translate ([0,0,-5.625]) camera(center=true);
//                %polyhedron(
//                    points = [
//                        [0,0,0],
//                        [10,0,0],
//                        [10,5,0],
//                        [0,5,0],
//                        [0,5,3],
//                        [10,5,3]  
//                    ],
//                    faces = [
//                        [0,1,2,3],
//                        [5,4,3,2],
//                        [0,4,5,1],
//                        [0,3,4],
//                        [5,2,1]
//                    ]
//                );
            }
            translate([0,10.5,-5]) cylinder(d = 1.75, h = 1.5, center = true);
            translate([0,-10.5,-5]) cylinder(d = 1.75, h = 1.5, center = true);
            translate([0,13.75,-6]) cube([30,2.5,8], center = true);
            translate([0,-13.75,-6]) cube([30,2.5,8], center = true);
        }
}

//This module puts everything together
module finalbody() {
    union() {
        body();
        rotate(5, v=[0,0,ssd/2]) {
            rotate([0,180,0]) translate([0,0,20]) clamp();
            rotate([0,180,0]) translate([0,0,20]) 
            rotate(a=5, v=[0,0,ssd/2]) translate([0,-ssd/50,0]) cameraholder();
        }
    }
}

if  (part == 0) {
    render() finalbody();
}
else if (part == 1) {
    render() body();
}
else if (part == 2) {
    render() cameraholder();
}
else if (part == 3) {
    render() clamp();
}
else {
    echo("<font color='red'>Error: You must select a valid part to print</font>")
    assert(false);
}