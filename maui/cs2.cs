using System;
using System.Security.Cryptography;

namespace MauiApp2
{
    public partial class MainPage : ContentPage
    {
        private Random random = new Random();
        private int s1, s2, s3;
        private Color total;

        public MainPage()
        {
            InitializeComponent();
        }

        private void start()
        {
            s1 = random.Next(0, 256);
            s2 = random.Next(0, 256);
            s3 = random.Next(0, 256);
            total = Color.FromRgb(s1, s2, s3);
            generate.Background = total;
        }

        private void generate_Clicked(object sender, EventArgs e)
        {
            start();
        }
    }
}
