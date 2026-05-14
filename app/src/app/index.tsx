import { View } from "react-native";
import { Button, Text } from "heroui-native";
import { useRecipes } from "@/lib/hooks";
import { LegendList } from "@legendapp/list";

function RecipeList() {
  const { data, error, isLoading, fetchNextPage } = useRecipes();

  if (isLoading) {
    return <Text>Loading...</Text>;
  }

  if (error) {
    console.error(error);
    return null;
  }

  const items = data?.pages?.flatMap((p: any) => p.items) ?? [];

  return (
    <LegendList
      data={items}
      renderItem={({ item }) => <Text>{item.title}</Text>}
      keyExtractor={(item) => item.id}
      onEndReached={() => fetchNextPage?.()}
      onEndReachedThreshold={0.5}
      onStartReachedThreshold={0.5}
      recycleItems
    />
  );
}

export default function Index() {
  return (
    <View className="flex-1 bg-background p-safe">
      <View className="w-full items-center py-4">
        <Text.Heading>Instachef</Text.Heading>
      </View>
      <View className="flex-1 justify-center items-center ">
        <RecipeList />
        <Button onPress={() => console.log("Pressed!")}>Get Started</Button>
      </View>
    </View>
  );
}
