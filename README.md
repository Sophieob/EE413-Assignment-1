# EE413-Assignment-1
EE413 Assignment 1 using UR5-e series robot and RealSense depth camera with Python with OpenCV, by Janam Pandya and Sophie O'Brien

## Industrial Application 
### Post-Harvest Produce Grading and Packaging
After harvest, fresh produce must be sorted by quality before it can be packed and sent to retail. Fruit that is ripe and ready to sell, fruit that needs more time to ripen and fruit that is damaged or rotting all need to go to different places. A single rotten item packed within good stock can spoil the entire box; The Food and Agriculture Organisation estimates that in 2011 around 30% of the world's food was lost or wasted every year. 

### Our Solution
We built a robotic system and packaging cell around the UR5e robot arm using a RealSense depth camera which watches a mixed pile of incoming produce and the robot sorts each item by quality grade (colour) and stacks it in its own pallet position. 

| In our demonstration | In a real packaging environment |
|----------------------|---------------------------------|
| Red blocks           | Ripe produce                    |
| Yellow blocks        | Under-ripe produce              |
| Blue blocks          | Rotten or damaged produce       |
| Other colour         | Unknown (HRI requirement)       |
| Conveyer             | Packaging environment transfer line |
| Stacks at different positions| Palletising by grade |
| Inspection station   | Manual quality check location |

The camera's colour detection will tell the robot the quality grade and it's depth information will tell it the items shape and height. The robot will then be able to pick up an item from the mixed grade pile and move it along the conveyer and stack it in the correct pallet for its grade. 

### Inclusive Design
Because the robot does the lifting, reaching and stacking, the operator's role is entirely  seated with no physical effort required. Therefore, quality inspection could be done by older workers, people with limited mobility or strength, or anyone for whom standing packaging work isn't possible. 
