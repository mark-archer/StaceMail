using SendGrid;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Net.Mail;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;

namespace StaceMail
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        public MainWindow()
        {
            InitializeComponent();
        }

        private void SendEmails_Click(object sender, RoutedEventArgs e)
        {
            var body = @"
another test

On Fri, Sep 19, 2014 at 6:05 PM, Mark Archer <mmadink@gmail.com> wrote:
test

On Fri, Sep 19, 2014 at 6:04 PM, <mmadink@gmail.com> wrote:
test
test 

";

            SendEmail(
                from: "mmadink@gmail.com", 
                to: new String[]{"mark_archer@live.com"}, 
                subject: "Re: StaceMail", 
                body: body);
        }

        private void SendEmail(string from, string[] to, string subject, string body, bool html_body = true)
        {            
            // Create an email, passing in the the eight properties as arguments.
            var email = new SendGridMessage();
            email.From = new MailAddress(from);
            email.To = to.Select(s => new MailAddress(s)).ToArray();
            email.Subject = subject;
            if (html_body)
                email.Html = body;
            else
                email.Text = body;
            
            SendEmail(email);
        }

        public static void SendEmail(SendGridMessage myMessage)
        {
            var credentials = new NetworkCredential("mmadink@gmail.com", "Echilon3");
            var transportWeb = new Web(credentials);
            transportWeb.Deliver(myMessage);            
        }

        
    }
}
