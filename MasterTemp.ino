#include "OneWire.h"
#include "DallasTemperature.h"
// Use EtherCard to enable ENC28J20 ethernet module
// Documentation: http://jeelabs.net/pub/docs/ethercard/classEtherCard.html
#include "EtherCard.h"
#include "net.h"
// Use EEPROM to store the network configuration
#include "EEPROM.h"
#include "NetEEPROM.h"

#define DEBUG 1

#define ETH_SPI_CHIP_SELECT_PIN 53
#define HOSTNAME_MAX_SIZE 50

#define TEMP_RESOLUTION_BITS 10 // 9, 10, 11 or 12 bits resolution with
// 93.75ms, 187.5ms, 375ms and 750ms temperature
// reading time respectively.

#define TEMP_P1_FL_PIN 16   // Temperature sensor Plane 1 (P1), Front-Left (FL)
#define TEMP_P1_FR_PIN 17   // Temperature sensor Plane 1 (P1), Front-Right (FR)
#define TEMP_P1_RL_PIN 18   // Temperature sensor Plane 1 (P1), Rear-Left (RL)
#define TEMP_P1_RR_PIN 19   // Temperature sensor Plane 1 (P1), Rear-Right (RR)
#define TEMP_P2_FL_PIN 20
#define TEMP_P2_FR_PIN 21
#define TEMP_P2_RL_PIN 22
#define TEMP_P2_RR_PIN 23
#define TEMP_P3_FL_PIN 24
#define TEMP_P3_FR_PIN 25
#define TEMP_P3_RL_PIN 26
#define TEMP_P3_RR_PIN 27
#define TEMP_P4_FL_PIN 28
#define TEMP_P4_FR_PIN 29
#define TEMP_P4_RL_PIN 30
#define TEMP_P4_RR_PIN 31
#define TEMP_P5_FL_PIN 32
#define TEMP_P5_FR_PIN 33
#define TEMP_P5_RL_PIN 34
#define TEMP_P5_RR_PIN 35

#define TEMPSENSORNAME_STR_LENGTH 6

byte oneWirePins[] = {
  TEMP_P1_FL_PIN, TEMP_P1_FR_PIN, TEMP_P1_RL_PIN, TEMP_P1_RR_PIN,
  TEMP_P2_FL_PIN, TEMP_P2_FR_PIN, TEMP_P2_RL_PIN, TEMP_P2_RR_PIN,
  TEMP_P3_FL_PIN, TEMP_P3_FR_PIN, TEMP_P3_RL_PIN, TEMP_P3_RR_PIN,
  TEMP_P4_FL_PIN, TEMP_P4_FR_PIN, TEMP_P4_RL_PIN, TEMP_P4_RR_PIN,
  TEMP_P5_FL_PIN, TEMP_P5_FR_PIN, TEMP_P5_RL_PIN, TEMP_P5_RR_PIN
};

String tempSensorName[] = {
  "P1_FL", "P1_FR", "P1_RL", "P1_RR",
  "P2_FL", "P2_FR", "P2_RL", "P2_RR",
  "P3_FL", "P3_FR", "P3_RL", "P3_RR",
  "P4_FL", "P4_FR", "P4_RL", "P4_RR",
  "P5_FL", "P5_FR", "P5_RL", "P5_RR"
};

const byte oneWirePinsCount = sizeof(oneWirePins) / sizeof(byte);
float *temperature = (float*)malloc(sizeof(float) * oneWirePinsCount);
unsigned int PREV_TCP_SEQ_NUM = 0;


OneWire temp_sensor_oneWire[oneWirePinsCount];
DallasTemperature temp_sensor[oneWirePinsCount];

// Array to store ethernet interface ip address
// Will be read by NetEEPROM
static byte myip[4];
// Array to store gateway ip address
// Will be read by NetEEPROM
static byte gwip[4];
// Array to store DNS IP Address
// Will be read by NetEEPROM
static byte dnsip[4];
// Array to store netmask
// Will be read by NetEEPROM
static byte netmask[4];
// Array to store ethernet interface mac address
// Will be read by NetEEPROM
static byte mymac[6];

// Used as cursor while filling the buffer
static BufferFiller bfill;

// TCP/IP send and receive buffer
byte Ethernet::buffer[2000];

void software_Reset() // Restarts program from beginning
{
  asm volatile ("  jmp 0");
}

 //get the sequence number of packets
unsigned int get_seq(byte *ethBuf) {
  unsigned int seq = 0;
  
  seq = (unsigned int)ethBuf[TCP_SEQ_H_P] << 24 |
        (unsigned int)ethBuf[TCP_SEQ_H_P+1] << 16 |
        (unsigned int)ethBuf[TCP_SEQ_H_P+2] << 8 |
        (unsigned int)ethBuf[TCP_SEQ_H_P+3];
        
  return seq;
}

// A function to print the MAC address
const void print_macAddress()
{
  for (byte i = 0; i < 6; ++i)
  {
    Serial.print(mymac[i], HEX);
    if (i < 5)
      Serial.print(':');
  }
}

/* A subnet mask must be composed of a sequence of one's (1)
   starting from the MSB, followed by a sequence of zeros (0).
   It can be something like 255.255.255.0, but not
   255.254.255.0. In the latter case, 254 equals to
   to the binary number 1111 1110 which is followed
   by 1111 1111 (255).
*/
bool subnet_mask_valid(byte subnet_mask[])
{
  byte i, j, test_mask;
  bool found_zero = false;

  for (i = 0; i < 4; i++)
  {
    test_mask = 0x80; //0b10000000

    for (j = 0; j < 8; j++)
    {
      //Serial.print("test_mask = ");
      //Serial.println(test_mask, HEX);
      /* If the bit is zero */
      if ((subnet_mask[i] & test_mask) == 0)
      {
        //Serial.print("0");
        /* If a zero hasn't been found yet */
        if (!found_zero)
          /* Once we found a 0, the found_zero flag
             is set to true. From now on, the of the
             bits should be zero.
          */
          found_zero = true;

        test_mask = (test_mask >> 1);
      }
      else
      {
        //Serial.print("1");
        /* if we run in this "else" clause
           it means that the current bit is "1"
           So if a zero has already been found,
           return false (not a valid subnet mask)
        */
        if (found_zero)
          return false;

        test_mask = (test_mask >> 1);
      }
    }
    //Serial.print(" ");
  }
  //Serial.println("");

  /* If the execution reached the end, it is a valid subnet mask*/
  return true;
}

void setup() {
#if DEBUG
  Serial.begin(115200);
  Serial.println("Dallas Temperature IC Control Library Demo");

  Serial.print("============ Ready with ");
  Serial.print(oneWirePinsCount);
  Serial.println(" Sensors ================");
#endif

  //Start up the library on all defined pins
  DeviceAddress deviceAddress;
  for (byte i = 0; i < oneWirePinsCount; i++) {
    
    temp_sensor_oneWire[i].setPin(oneWirePins[i]); 
    temp_sensor[i].setOneWire(&temp_sensor_oneWire[i]); 
    temp_sensor[i].begin(); 
#if DEBUG
    if (!temp_sensor[i].getAddress(deviceAddress, 0))
      Serial.println("Unable to find address for Device 0");
#endif

    temp_sensor[i].setResolution(deviceAddress, TEMP_RESOLUTION_BITS);
    temp_sensor[i].setWaitForConversion(false);
#if DEBUG
    Serial.print("Device Resolution on Pin ");
    Serial.print(oneWirePins[i]);
    Serial.print(": ");
    Serial.print(temp_sensor[i].getResolution(deviceAddress), DEC);
    Serial.println();
#endif
  }

  // To reset the ip configuration, write the value 0 to NET_EEPROM_OFFSET.
  // 0 is the offset
  //EEPROM.write(NET_EEPROM_OFFSET, 0);

  NetEeprom.init(mymac);
  
  Serial.print("MAC: ");
  print_macAddress();
  Serial.println();
  
  while (ether.begin(sizeof Ethernet::buffer, mymac, ETH_SPI_CHIP_SELECT_PIN) == 0)
  {
    Serial.println( "Failed to access Ethernet controller");
    delay(5000);
  }

  if (NetEeprom.isDhcp())
  {
    Serial.println("Try DHCP");
    if (!ether.dhcpSetup())
      Serial.println( "DHCP failed");
  }
  else
  {
    NetEeprom.readIp(myip);
    NetEeprom.readGateway(gwip);
    NetEeprom.readDns(dnsip);
    NetEeprom.readSubnet(netmask);
    Serial.println("Static IP");
    ether.staticSetup(myip, gwip, dnsip, netmask);
  }

  ether.printIp("My IP: ", ether.myip);
  ether.printIp("Netmask: ", ether.netmask);
  ether.printIp("GW IP: ", ether.gwip);
  ether.printIp("DNS IP: ", ether.dnsip);

//  while (ether.clientWaitingGw())
//    ether.packetLoop(ether.packetReceive());
//  Serial.println("Gateway found");
//  Serial.println("");
}

// function to print the temperature for a device
void printTemperature(float temperature, String sensor_name, byte pinConnectedTo)
{
#if DEBUG
  Serial.print("Temperature for the sensor ");
  Serial.print(sensor_name);
  Serial.print(" (Pin ");
  Serial.print(pinConnectedTo);
  Serial.print(") is ");
  Serial.println(temperature);
#endif
}

//$D = word data type
//$L = long data type
//$S = c string
//$F = progmem string
//$E = byte from the eeprom.
//$T = float type
const char http_OK_200[] PROGMEM =
  "HTTP/1.0 200 OK\r\n"
  "Content-Type: text/html\r\n"
  "Pragma: no-cache\r\n\r\n"
  ;

const char http_unauthorized_401[] PROGMEM =
  "HTTP/1.0 401 Unauthorized\r\n"
  "Content-Type: text/html\r\n\r\n"
  ;

const char http_not_found_404[] PROGMEM =
  "HTTP/1.0 404 Not Found\r\n"
  "Content-Type: text/html\r\n"
  "Pragma: no-cache\r\n\r\n"
  ;

const char webpage_unauthorized[] PROGMEM =
  "<!DOCTYPE HTML>\r\n"
  "<h1>401 Unauthorized</h1>"
  ;

const char webpage_not_found[] PROGMEM =
  "<!DOCTYPE HTML>\r\n"
  "<html><head>\r\n"
  "<title>404 Not Found</title>\r\n"
  "</head><body>\r\n"
  "<h1>Not Found</h1>\r\n"
  "<p>The requested URL /$S was not found on this server.</p>\r\n"
  "<hr>\r\n"
  "<address>Vaguino Web Server at $D.$D.$D.$D</address>\r\n"
  "</body></html>"
  ;

const char webpage_temperature[] PROGMEM =
  "$S=$S <br>"
  ;

const char webpage_ipconfig[] PROGMEM =
  "<!DOCTYPE HTML>\r\n"
  "<html><head>"
  "<title>IP Configuration</title>"
  "<style type=\"text/css\">\r\n"
  "a {"
  "color: #003399;"
  "background-color: transparent;"
  "font-weight: normal;"
  "text-decoration: none;"
  "}\r\n"
  "</style>\r\n"
  "<script src=\"http://code.jquery.com/jquery-latest.min.js\"></script>"
  "<script type=\"text/javascript\">"
  "$$(function() {"
  "enable_cb();"
  "$$(\"#g\").click(enable_cb);"
  "$$(\"input.g\").prop(\"disabled\", $$(\"#g\").prop('checked'));"
  "});"
  "function enable_cb() {"
  "$$(\"input.g\").prop(\"disabled\", this.checked);"
  "}"
  "</script>"
  "</head><body>"
  "<form method=\"post\">"
  "<table>"
  "<tr><td colspan=\"2\"><a href=\"http://$S\">Home</a></td></tr>"
  "<tr><td colspan=\"2\" align=\"right\"><input type=\"checkbox\" name=\"dhcp\" value=\"1\" id=\"g\" $S>Use DHCP</td></tr>"
  "<tr><td align=\"right\">IP Address:</td><td><input type=\"text\" name=\"ip\" class=\"g\" value=\"$D.$D.$D.$D\"></td></tr>"
  "<tr><td align=\"right\">Subnet mask:</td><td><input type=\"text\" name=\"subnet\" class=\"g\" value=\"$D.$D.$D.$D\"></td></tr>"
  "<tr><td align=\"right\">Gateway:</td><td><input type=\"text\" name=\"gw\" class=\"g\" value=\"$D.$D.$D.$D\"></td></tr>"
  "<tr><td align=\"right\">DNS Server:</td><td><input type=\"text\" name=\"dns\" class=\"g\" value=\"$D.$D.$D.$D\"></td></tr>"
  "<tr><td colspan=\"2\" align=\"right\"><input type=\"submit\" value=\"Submit and save\"></td></tr>"
  "</table>"
  "</form>"
  "</body></html>"
  ;

const char webpage_main[] PROGMEM =
  "<!DOCTYPE HTML>\r\n"
  "<html>"
  "<head>\r\n"
  "<title>RACK Temperature Meter with Arduino!</title>\r\n"
  "<style type=\"text/css\">\r\n"
  "::selection{ background-color: #E13300; color: white; }\r\n"
  "::moz-selection{ background-color: #E13300; color: white; }\r\n"
  "::webkit-selection{ background-color: #E13300; color: white; }\r\n"
  "body {"
  "background-color: #fff;"
  "margin: 40px;"
  "font: 15px/20px normal Helvetica, Arial, sans-serif;"
  "color: #4F5155;"
  "}\r\n"
  "a {"
  "color: #003399;"
  "background-color: transparent;"
  "font-weight: normal;"
  "text-decoration: none;"
  "}\r\n"
  "h1 {"
  "color: #444;"
  "background-color: transparent;"
  "border-bottom: 1px solid #D0D0D0;"
  "font-size: 19px;"
  "font-weight: normal;"
  "margin: 0 0 14px 0;"
  "padding: 14px 15px 10px 15px;"
  "}\r\n"
  "#contain {"
  "margin: 10px;"
  "border: 1px solid #D0D0D0;"
  "-webkit-box-shadow: 0 0 8px #D0D0D0;"
  "padding: 14px 15px 10px 15px;"
  "}\r\n"
  "p {"
  "margin: 12px 15px 12px 15px;"
  "}\r\n"
  ".boxed { box-shadow: 0 0 0 1px #eeeeee; font-size: 21px; font-weight: bold; color: #5a9bbb;}"
  "</style>\r\n"
  "</head>\r\n"
  "<body>\r\n"
  "<div id=\"contain\">\r\n"
  "<h1>Welcome to the RACK Temperature Meter webserver made with Arduino</font></h1>\r\n"
  "<p><a href=\"http://$S/ipconfig\">IP Configuration</a></p>"
  "<p><a href=\"http://$S/temp\">Rack Temperatures</a></p>"
  "</div>\r\n"
  "</body>\r\n"
  "</html>"
  ;

const char webpage_please_connect_manually[] PROGMEM =
  "Please connect manually to the newly configured IP address."
  ;

void get_hostname_from_http_request(char data[], char hostname[], int hostname_size)
{
  int i;
  /* Whenever a new line is found
     end_of_line becomes true;

     The hostname should start right after
     a '\r\n' in the beginning of a new line.
  */
  bool end_of_line = false;

  for (i = 0; i < strlen(data); i++)
  {
    /* If we are in the middle of a line,
       keep on searching until a \r\n is found.
    */
    if (!end_of_line)
    {
      if (data[i] == '\r')
      {
        if (data[++i] == '\n')
        {
          /* if found, set end_of_line = true*/
          end_of_line = true;
        }
      }
    }
    else
    {
      /* The code runs in this else case whenever a new line is starting */
      end_of_line = false;
      /* If the line starts with 'Host: ', the it should be our line! */
      if (data[i] == 'H' && data[i + 1] == 'o' && data[i + 2] == 's' && data[i + 3] == 't' && data[i + 4] == ':' && data[i + 5] == ' ')
      {
        i += 6;
        int j;
        for (j = 0; j < hostname_size; j++)
        {
          /* So read the hostname and store it in the hostname char array
             until the next line comes,
          */
          if (data[i] == '\r' && data[i + 1] == '\n')
          {
            hostname[j] = '\0';
            return;
          }


          hostname[j] = data[i++];
        }
      }
    }
  }
}

void loop() {
  // Copy received packets to data buffer Ethernet::buffer
  // and return the uint16_t Size of received data (which is needed by ether.packetLoop).
  word len = ether.packetReceive();
  // Parse received data and return the uint16_t Offset of TCP payload data
  // in data buffer Ethernet::buffer, or zero if packet processed
  word pos = ether.packetLoop(len);

  if (pos) {
    // Store the received request data in the *data pointer
    unsigned int CURRENT_TCP_SEQ_NUM = get_seq(Ethernet::buffer);
    
    Serial.print("PREV TCP SEQ: ");
    Serial.print(PREV_TCP_SEQ_NUM);
    Serial.print(", CURRENT_TCP_SEQ_NUM: ");
    Serial.println(CURRENT_TCP_SEQ_NUM);    
    
    char *data = (char *) Ethernet::buffer + pos;
    // Store the IP of the connect client in the *clientIP pointer
    byte *clientIP = (byte *) Ethernet::buffer + IP_SRC_P;

    // bfill stores a Pointer to the start of TCP payload.
    bfill = ether.tcpOffset();
    if (PREV_TCP_SEQ_NUM != CURRENT_TCP_SEQ_NUM) {
      PREV_TCP_SEQ_NUM = CURRENT_TCP_SEQ_NUM;
      /* Use the 'hostname_client_connected' array to store the hostname that the client is using
         and use this hostname for the links.
         Initially I was using the IP of the ENC28J60 module, but I found out that if I connect
         from the Internet using a dyndns, this doesn't work because the IP is usually in a private
         192.168.x.x range, which is not publicly routable.
      */
      char hostname_client_connected[HOSTNAME_MAX_SIZE];
      memset(hostname_client_connected, '\0', sizeof(char) * HOSTNAME_MAX_SIZE);
  
      ether.printIp("Got connection from: ", clientIP);
  
      //Serial.println(data);
  
      /* Temporary string to store the values read from the http request */
      char str_temp[20];
      if (strncmp("GET /", data, 5) == 0)
      {
        get_hostname_from_http_request(data, hostname_client_connected, HOSTNAME_MAX_SIZE);
        //Serial.println(hostname_client_connected);
  
        data += 5;
        if (data[0] == ' ')
        {
          bfill.emit_p(http_OK_200);
          bfill.emit_p(webpage_main, 
                       hostname_client_connected,
                       hostname_client_connected
                       );
        } else if (strncmp( "temp ", data, 5 ) == 0) {
          Serial.println("Requesting Temperatures...");
          //for (int i = 0; i < 1; i++)
          for (int i = 0; i < oneWirePinsCount; i++)
            temp_sensor[i].requestTemperatures();
  
          switch (TEMP_RESOLUTION_BITS){
            case 9:
              delay(94);
              break;
            case 10:
              delay(188);
              break;
            case 11:
              delay(375);
              break;
            default:
              Serial.println("Unknown resolution...");
            case 12:
              delay(750);
              break;
            }
          //Serial.println("Requesting Temperatures Done...");
          bfill.emit_p(http_OK_200);
          for (int i = 0; i < oneWirePinsCount; i++) {
          //for (int i = 0; i < 1; i++) {
            temperature[i] = temp_sensor[i].getTempCByIndex(0);
            tempSensorName[i].toCharArray(str_temp, TEMPSENSORNAME_STR_LENGTH);
            bfill.emit_p(webpage_temperature,
                         str_temp,
                         dtostrf(temperature[i], 4, 2, str_temp + TEMPSENSORNAME_STR_LENGTH));
            //printTemperature(temperature[i], tempSensorName[i], oneWirePins[i]);
          }
          //Serial.println("Added to network buffer done...");
        }
        else if (strncmp( "ipconfig ", data, 9 ) == 0)
        {
          NetEeprom.readIp(myip);
          NetEeprom.readGateway(gwip);
          NetEeprom.readDns(dnsip);
          NetEeprom.readSubnet(netmask);
  
          bfill.emit_p(http_OK_200);
          char checked_dhcp[8] = "";
          if (NetEeprom.isDhcp())
            strcat(checked_dhcp, "checked\0");
  
          bfill.emit_p(webpage_ipconfig,
                       hostname_client_connected,
                       checked_dhcp,
                       myip[0], myip[1], myip[2], myip[3],
                       netmask[0], netmask[1], netmask[2], netmask[3],
                       gwip[0], gwip[1], gwip[2], gwip[3],
                       dnsip[0], dnsip[1], dnsip[2], dnsip[3]);
  
        }
        else
        {
          int i;
          for ( i = 0; i < sizeof(str_temp) - 1; i++ )
          {
            if (data[i] == ' ')
            {
              str_temp[i] = '\0';
              break;
            }
            str_temp[i] = data[i];
          }
          bfill.emit_p(http_not_found_404);
          bfill.emit_p(webpage_not_found, str_temp, ether.myip[0], ether.myip[1], ether.myip[2], ether.myip[3]);
        }
      }
      else if (strncmp("POST /ipconfig ", data, 14) == 0)
      {
        //Serial.println(data);
        get_hostname_from_http_request(data, hostname_client_connected, HOSTNAME_MAX_SIZE);
        //Serial.print("Client connected to: ");
        //Serial.println(hostname_client_connected);
  
        int datalen = strlen(data);
  
        //Serial.print("Data length: ");
        //Serial.println(datalen);
  
        /* Find the offset that the POSTed data start */
        while (data[datalen--] != '\n')
          continue;
  
        data += (datalen += 2);
  
        //Serial.println(data);
        //Serial.println(strlen(data));
  
        int i, j = 0;
        /* if read_var_name == true, then we parse the name of the variable we want to read
           i.e. ip, dns, subnet or gw
           if read_var_name == false, then we parse the value for the previously read var_name
        */
        bool read_var_name = true;
        /* If the configuration parameters are ok,
           set the corresponding IP addresses
        */
        bool static_conf_ok = true;
        char value[20];
        if (strlen(data) == 0) {
          len = ether.packetReceive();
          pos = ether.packetLoop(len);
          data = (char *) Ethernet::buffer + pos;
          // Serial.print("Second read: ");
          // Serial.println(data);
        }
          
        for ( i = 0; i <= strlen(data); i++ )
        {
          /* if we read '=', then the value should follow */
          if (data[i] == '=')
          {
            /* so add a string termination character i nthe str_temp */
            str_temp[j] = '\0';
            j = 0;
            /* set the read_var_name=false */
            read_var_name = false;
            continue;
          }
  
          /* if the current character is '&', or the string termination character '\0'
             which marks the end of the available data, then the value reading has finished
             and we can start reading the next variable (if more variables exist) and process
             the current one
          */
          if (data[i] == '&' || data[i] == '\0')
          {
            /* so terminate the value string */
            value[j] = '\0';
            j = 0;
            /* enable the flag read_var_name so that we can start reading a
               variable name in the next loop
            */
            read_var_name = true;
            if (strncmp(str_temp, "dhcp", 4) == 0)
            {
              // Serial.print("dhcp: ");
              // Serial.println(value);
              /* If it is not set already to DHCP, do it now.
                 and set the static_conf_ok = false since we
                 configure the ip address setting by using DHCP
              */
              static_conf_ok = false;
              if (!NetEeprom.isDhcp())
              {
                NetEeprom.writeDhcpConfig(mymac);
  
                bfill.emit_p(http_OK_200);
                bfill.emit_p(webpage_please_connect_manually);
                ether.httpServerReply(bfill.position());
  
                software_Reset();
              }
            }
            else if (strncmp(str_temp, "ip", 2) == 0)
            {
              //Serial.print("ip: ");
              //Serial.println(value);
              if (ether.parseIp(myip, value) != 0)
              {
                static_conf_ok = false;
                break;
              }
            }
            else if (strncmp(str_temp, "gw", 2) == 0)
            {
              //Serial.print("gw: ");
              //Serial.println(value);
              if (ether.parseIp(gwip, value) != 0)
              {
                static_conf_ok = false;
                break;
              }
            }
            else if (strncmp(str_temp, "dns", 3) == 0)
            {
              //Serial.print("dns: ");
              //Serial.println(value);
              if (ether.parseIp(dnsip, value) != 0)
              {
                static_conf_ok = false;
                break;
              }
            }
            else if (strncmp(str_temp, "subnet", 6) == 0)
            {
              //Serial.print("subnet: ");
              //Serial.println(value);
              if (ether.parseIp(netmask, value) != 0)
              {
                static_conf_ok = false;
                break;
              }
              else
              {
                //Serial.println("subnet is a valid IP");
                /* It is not enough for the subnet mask
                   to be a valid IP address.
                   It needs to follows some additional
                   rules, so call subnet_mask_valid()
                   function to make sure it is a valid
                   subnet mask.
                */
                if (!subnet_mask_valid(netmask))
                {
                  Serial.println("subnet is not a valid mask!");
                  static_conf_ok = false;
                  break;
                }
  
              }
            }
  
            if (data[i] == ' ')
              break;
            else
              continue;
          }
  
          if (data[i] != '=')
          {
            if (read_var_name)
              str_temp[j++] = data[i];
            else
              value[j++] = data[i];
          }
        }
  
        if (static_conf_ok)
        {
          NetEeprom.writeManualConfig(mymac, myip, gwip, netmask, dnsip);
  
          bfill.emit_p(http_OK_200);
          bfill.emit_p(webpage_please_connect_manually);
          ether.httpServerReply(bfill.position());
  
          software_Reset();
        }
  
        NetEeprom.readIp(myip);
        NetEeprom.readGateway(gwip);
        NetEeprom.readDns(dnsip);
        NetEeprom.readSubnet(netmask);
  
        bfill.emit_p(http_OK_200);
        char checked_dhcp[8] = "";
        if (NetEeprom.isDhcp())
          strcat(checked_dhcp, "checked\0");
  
        bfill.emit_p(webpage_ipconfig,
                     hostname_client_connected,
                     checked_dhcp,
                     myip[0], myip[1], myip[2], myip[3],
                     netmask[0], netmask[1], netmask[2], netmask[3],
                     gwip[0], gwip[1], gwip[2], gwip[3],
                     dnsip[0], dnsip[1], dnsip[2], dnsip[3]);
  
      }
      else
      {
        bfill.emit_p(http_unauthorized_401);
        bfill.emit_p(webpage_unauthorized);
      }
      // Send a response to an HTTP request.
      //Serial.println("Sending response back to the client...");
      ether.httpServerReply(bfill.position());
    } else {
      bfill.emit_p(http_OK_200);
      ether.httpServerReply(bfill.position());
      //Serial.println("Duplicate request. The received TCP packet has already been served.");
    }
  }
}
