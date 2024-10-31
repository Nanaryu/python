namespace MauiApp2
{
    public partial class MainPage : ContentPage
    {
        int count = 0;

        public MainPage()
        {
            InitializeComponent();
        }
        private void add(object sender, EventArgs e)
        {
            var control = sender as Button;
            field.Text += control.Text;
        }
        private void clear(object sender, EventArgs e)
        {
            field.Text = "0";
        }
        private void plus(object sender, EventArgs e)
        {
            prev.Text += " + " + field.Text;
            operation.Text = "+";
        }
        private void equal(object sender, EventArgs e)
        {
            int x1, x2;
            int.TryParse(field.Text, out x1);
            int.TryParse(prev.Text, out x1);
            field.Text = x1 + x2;
        }
    }

}
