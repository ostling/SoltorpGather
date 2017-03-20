CREATE TABLE IF NOT EXISTS `rain`(
`id` int(255) NOT NULL AUTO_INCREMENT,
 
`ticks` int(255)  NOT NULL,

`mmAccumulated` double NOT NULL,
 
`dateMeasured` date NOT NULL,
 
`timeMeasured` time NOT NULL,
  
PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;
