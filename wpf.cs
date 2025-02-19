using System.Text;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;

namespace WpfApp1
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        private Random rnd;
        private int boxes = 1;
        public MainWindow()
        {
            InitializeComponent();
            rnd = new Random();
        }

        private void Button_Click(object sender, RoutedEventArgs e)
        {
            string t = "";
            t = t1.Text;
            t1.Text = t2.Text;
            t2.Text = t;
        }

        private void Button_MouseEnter(object sender, MouseEventArgs e)
        {
            //b1.Margin = new Thickness(rnd.Next(1, 200), rnd.Next(1, 100), rnd.Next(1, 200), rnd.Next(1, 100));
        }

        private void b2_Click(object sender, RoutedEventArgs e)
        {
            l1.Content = boxes;
            CheckBox check = new CheckBox();
            check.Name = $"c{2^boxes}";
            check.Margin = new Thickness(boxes * 10, 0, 0, 0);
            check.HorizontalAlignment = HorizontalAlignment.Left;
            check.VerticalAlignment = VerticalAlignment.Center;
            boxes += 1;
        }

        private void chck(object sender, RoutedEventArgs e)
        {
            CheckBox check = (CheckBox)sender;
            int x = 0;
            int l = 0;
            Int32.TryParse(check.Name.Remove(0), out x);
            Int32.TryParse(l2.Content, out l);
            if (check.IsChecked)
            {
                l2.Content = l + x;
            }
            else
            {
                l2.Content = l - x;
            }
        }
    }
}
