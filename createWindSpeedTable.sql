CREATE TABLE IF NOT EXISTS `wind_speed`(
`id` int(255) NOT NULL AUTO_INCREMENT,
 
`wind_speed` VARCHAR(10) NOT NULL,
 
`dateMeasured` date NOT NULL,
 
`timeMeasured` time NOT NULL,
  
PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;
