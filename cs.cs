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
    }

}
