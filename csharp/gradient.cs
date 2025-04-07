namespace MauiApp2
{
    public partial class MainPage : ContentPage
    {
        public MainPage()
        {
            InitializeComponent();
        }
        private bool isAnimating = true;

        private async void Button_Clicked(object sender, EventArgs e)
        {
            
            Color[] colors =
            {
                Colors.Red,
                Colors.Blue,
                Colors.Violet,
                Colors.DarkViolet,
                Colors.DeepPink,
                Colors.LightGoldenrodYellow,
                Colors.LightGreen,
                Colors.LightPink
            };

            while (isAnimating)
            {
                for (int i = 0; i < colors.Length - 1; i++)
                {
                    gradientB.GradientStops[0].Color = colors[i];

                    if (i + 1 <= colors.Length - 1)
                        gradientB.GradientStops[1].Color = colors[i + 1];
                    else
                        gradientB.GradientStops[1].Color = colors[0];

                    if (i + 2 <= colors.Length - 2)
                        gradientB.GradientStops[2].Color = colors[i + 2];
                    else
                        gradientB.GradientStops[2].Color = colors[1];

                    if (i + 3 <= colors.Length - 2)
                        gradientB.GradientStops[3].Color = colors[i + 3];
                    else
                        gradientB.GradientStops[3].Color = colors[2];

                    await Task.Delay(100);
                }
            }
        }

        private void Button_Clicked_1(object sender, EventArgs e)
        {
            isAnimating = !isAnimating;
        }
    }
}
